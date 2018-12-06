package com.example.mohammadmuntasir.myapplication;

import android.os.Bundle;
import android.support.wearable.activity.WearableActivity;
import android.widget.TextView;
import java.util.concurrent.TimeUnit;
import android.os.Handler;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

import android.net.wifi.WifiManager;
import java.util.Formatter;

import java.net.NetworkInterface;
import java.util.Enumeration;
import java.net.InetAddress;
import android.app.NotificationManager;

import android.content.Context;
import android.text.format.Time;
import java.io.DataInputStream;
import java.util.Calendar;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Random;
import android.os.BatteryManager;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.net.MalformedURLException;
import java.net.HttpURLConnection;
import android.graphics.Color;
import java.io.DataOutputStream;
import android.os.AsyncTask;
import android.util.Log;
import android.app.NotificationChannel;
import android.support.v4.app.NotificationCompat;
import android.support.v4.app.NotificationCompat.Builder;
import android.content.Intent;
import android.app.TaskStackBuilder;
import android.app.PendingIntent;
import android.media.MediaPlayer;
import android.view.Gravity;
import android.net.Uri;
import android.media.RingtoneManager;
import android.media.Ringtone;
import android.provider.Settings;
import android.view.View;
import android.widget.RelativeLayout;
import android.widget.LinearLayout;
import android.view.MotionEvent;
public class MainActivity extends WearableActivity {

    private TextView mTextView;
    private ServerSocket serverSocket;
    Handler updateConversationHandler;
    Thread serverThread = null;
    TextView message;
    String recent = "No signal";
    int ns = 2;
    int dq = 0;
    int dl = 5;
    Time mytime;
    Handler handler;
    Runnable r;
    String nowZone = "No signal";
    public static final int port = 1095;

    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mTextView = (TextView) findViewById(R.id.text);
        // Enables Always-on
        setAmbientEnabled();
        message = (TextView) findViewById(R.id.message);
        updateConversationHandler = new Handler();
        WifiManager wm = (WifiManager) getSystemService(WIFI_SERVICE);
        String str = "STARTING!!!";
        Log.d("Tag","Starts here");
        message.setText(str);
        message.setTextSize(22);
        message.setY(1);
        mytime = new Time();

        r = new Runnable() {
            @Override
            public void run() {
                setTime(); // calls the main function every 1 second
                handler.postDelayed(r, 1000);
            }
        };

        handler = new Handler();
        handler.postDelayed(r,1000);




        String zone = "";

    }


    public void setTime() { // the main function
        DateFormat df = new SimpleDateFormat("MM/dd/yyyy HH:mm:ss"); // gets date and time
        Date today = Calendar.getInstance().getTime();
        String reportDate = df.format(today);
        BatteryManager bm = (BatteryManager)getSystemService(BATTERY_SERVICE);
        int batLevel = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
        Random Rand = new Random();
        //int idx = Rand.nextInt(3);
        String[] zones = {"safe", "warning", "danger"};
        String[] colors = {"#808080","#00FF00","#FFFF00","#FF0000"};
        GetContents gc = new GetContents(); // VERY IMPORTANT THIS GETS THE MESSAGE FROM THE SERVER HOSTED BY THE PC PROGRAM
        gc.execute("nothingß");
        int idx = 0;
        int zoneNum = Character.getNumericValue(nowZone.charAt(0));
        if(zoneNum == 1){ // hallway
            idx = 2;
            if(dq > 0 && ns == 0){
                dq--; // dq is the danger level
            }
        }
        if(zoneNum == 0){ // bedroom
            idx = 1;
            if(dq > 0 && ns == 0){
                dq--;
            }
        }
        if(zoneNum == 2){ // front door
            idx = 3;
            if(dq < dl && ns == 0){ // dl is the danger limit
                dq++;
            }
            if(dq == dl && ns == 0){ // dq reached dl so we alert the user
                dq = 0;
                String notifdesp = "The patient was at the Front Door " + reportDate.substring(11,reportDate.length());
                notifyThis("Danger", notifdesp); // calls the notification methods
                playSound(); // plays the ringtone
            }
        }
        String str = "Date: " + reportDate.substring(0,6) + reportDate.substring(8,10) + "\nTime: " + reportDate.substring(11,reportDate.length()) + "\n" + nowZone.substring(1,nowZone.length()); // displays the message
        message.setGravity(Gravity.CENTER);
        Log.d("Wandering", "Danger lvl is " + Integer.toString(dq));
        message.setTextColor(Color.parseColor(colors[idx]));
        message.setText(str); // sets the text
    }

    @Override
    protected void onStop() {
        super.onStop();
        try {
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private class GetContents extends AsyncTask<String, Void, String> { // reads the message on the flask server hosted by the pc program
        protected String doInBackground(String... p) {
            String targetURL = p[0];
            //String urlParameters = p[1];
            URL url;
            HttpURLConnection connection = null;
            Socket          socket   = null;
            ServerSocket    server   = null;
            DataInputStream in       =  null;


            try {
                // http://192.168.1.105:6991/
                // 192.168.0.13
                url = new URL("http://192.168.0.13:6991/");

                // Get the input stream through URL Connection
                URLConnection con = url.openConnection();
                InputStream is = con.getInputStream();

                BufferedReader br = new BufferedReader(new InputStreamReader(is));

                String line = null;

                // read each line and write to System.out
                while ((line = br.readLine()) != null) {
                    Log.d("TAG", line);
                    //message.setText(line);
                    nowZone = line;
                    recent = line;
                    if(ns > 0){
                        ns--;
                    }
                }
                return line;
            } catch (IOException e) {
                Log.d("TAG", "nothing");
                nowZone = "3No signal";
                if(ns < 2){
                    ns++;
                    nowZone = recent;
                }
                return null;
            }


        }
        protected void onPostExecute(String result) {
            // do something
        }
    }

    public void playSound(){ // plays the ring tone
        Log.d("Sound", "step 1");
        Uri notification = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        Ringtone r = RingtoneManager.getRingtone(getApplicationContext(), notification);
        r.play();

        final MediaPlayer player = MediaPlayer.create(this,
                Settings.System.DEFAULT_RINGTONE_URI);

        MediaPlayer mMediaPlayer = new MediaPlayer();
        mMediaPlayer = MediaPlayer.create(this, R.raw.wearnotif);

        player.start();
        Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            public void run() {
                player.stop();
            }
        }, ((dl-1)*1000));
        Log.d("Sound", "Sound is played");

    }
    public void notifyThis(String title, String message) { // sends a notification
        int NOTIFICATION_ID = 234;

        NotificationManager notificationManager = (NotificationManager) this.getSystemService(Context.NOTIFICATION_SERVICE);


            String CHANNEL_ID = "my_channel_01";
            CharSequence name = "my_channel";
            String Description = "This is my channel";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel mChannel = new NotificationChannel(CHANNEL_ID, name, importance);
            mChannel.setDescription(Description);
            mChannel.enableLights(true);
            mChannel.setLightColor(Color.RED);
            mChannel.enableVibration(true);
            mChannel.setVibrationPattern(new long[]{100, 200, 300, 400, 500, 400, 300, 200, 400});
            mChannel.setShowBadge(true);
            notificationManager.createNotificationChannel(mChannel);


        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setDefaults(NotificationCompat.DEFAULT_ALL)
                .setSmallIcon(R.drawable.notif)
                .setContentTitle(title)
                .setContentText(message)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_MESSAGE)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC);//to show content in lock screen



        Intent resultIntent = new Intent(this, MainActivity.class);
        TaskStackBuilder stackBuilder = TaskStackBuilder.create(this);
        stackBuilder.addParentStack(MainActivity.class);
        stackBuilder.addNextIntent(resultIntent);
        PendingIntent resultPendingIntent = stackBuilder.getPendingIntent(0, PendingIntent.FLAG_UPDATE_CURRENT);

        builder.setContentIntent(resultPendingIntent);

        notificationManager.notify(NOTIFICATION_ID, builder.build());
        Log.d("TAG", "Notification is built");
    }
}


