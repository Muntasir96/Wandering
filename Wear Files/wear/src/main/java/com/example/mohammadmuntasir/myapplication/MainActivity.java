package com.example.mohammadmuntasir.myapplication;

import android.os.Bundle;
import android.support.wearable.activity.WearableActivity;
import android.widget.TextView;
import android.os.Handler;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import android.net.wifi.WifiManager;
import android.app.NotificationManager;

import android.content.Context;
import android.text.format.Time;
import java.util.Calendar;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import android.os.BatteryManager;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import android.graphics.Color;
import android.os.AsyncTask;
import android.util.Log;
import android.app.NotificationChannel;
import android.support.v4.app.NotificationCompat;
import android.content.Intent;
import android.app.TaskStackBuilder;
import android.app.PendingIntent;
import android.media.MediaPlayer;
import android.view.Gravity;
import android.net.Uri;
import android.media.RingtoneManager;
import android.media.Ringtone;
import android.provider.Settings;

public class MainActivity extends WearableActivity {

    private TextView mTextView;
    Handler updateConversationHandler;
    TextView message;
    String recent = "4No signal"; // 4 means greay color
    Time mytime;
    Handler handler;
    Runnable r;
    String nowZone = "4No signal";
    
    String ip = "192.168.1.105"; // THIS IS IP ADDRESS OF HOST SERVER FROM PC
    int port = 6991; // THIS IS PORT NUMBER FROM HOST SERVER FROM PC
    
    @Override
    protected void onCreate(Bundle savedInstanceState){
        
        // Initialize text and processes
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

        // Runs the main function: SetTime() every 1 second
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
        
        BatteryManager bm = (BatteryManager)getSystemService(BATTERY_SERVICE); // battery
        String[] colors = {"#00FF00","#FFFF00", "#FF0000" ,"#FF0000", "#808080"}; // [green, yellow, red, red, gray]
        
        GetContents gc = new GetContents(); // VERY IMPORTANT THIS GETS THE MESSAGE FROM THE SERVER HOSTED BY THE PC PROGRAM
        gc.execute("nothing");
        
        int zoneNum = Character.getNumericValue(nowZone.charAt(0)); // code from the server
        if(zoneNum == 3){ // 3 means red color AND ALERT THE WATCH
            String notifdesp = "The patient was at the Front Door " + reportDate.substring(11,reportDate.length()); // write notification
            notifyThis("Danger", notifdesp); // calls the notification methods
            playSound(); // plays the audiofile
        }
        
        // set text, position, and color
        String str = "Date: " + reportDate.substring(0,6) + reportDate.substring(8,10) + "\nTime: " + reportDate.substring(11,reportDate.length()) + "\n" + nowZone.substring(1,nowZone.length()); // displays the message
        message.setGravity(Gravity.CENTER);
        message.setTextColor(Color.parseColor(colors[zoneNum]));
        message.setText(str); // sets the text
    }


    private class GetContents extends AsyncTask<String, Void, String> { // reads the message on the flask server hosted by the pc program
        protected String doInBackground(String... p) {
            String targetURL = p[0];
            URL url;
            try { // the server is up
                url = new URL("http://" + ip + ":" + Integer.toString(port)); // reads the server
                
                // open connection
                URLConnection con = url.openConnection();
                InputStream is = con.getInputStream();

                BufferedReader br = new BufferedReader(new InputStreamReader(is));

                String line = null;

                while ((line = br.readLine()) != null) {
                    Log.d("TAG", line);
                    //message.setText(line);
                    nowZone = line; // nowZone will be used in setTime()
                    recent = line; // set the most recent zone to the message
                }
                return line;
            } catch (IOException e) { // server is down
                Log.d("TAG", "nothing");
                nowZone = recent; // get the most recent zone
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

        //final MediaPlayer player = MediaPlayer.create(this,
        //                Settings.System.DEFAULT_RINGTONE_URI); // RING TONE

        final MediaPlayer player = MediaPlayer.create(this,
                R.raw.wearnotif); // AUDIO FILE

        player.start();
        Handler handler = new Handler();
        handler.postDelayed(new Runnable() { // PLAYS THE AUDIO FILE FOR 5 SECONDS
            public void run() {
                player.stop();
            }
        }, (5*1000));
        Log.d("Sound", "Sound is played");

    }
    public void notifyThis(String title, String message) { // sends a notification
        int NOTIFICATION_ID = 234;

        NotificationManager notificationManager = (NotificationManager) this.getSystemService(Context.NOTIFICATION_SERVICE);

            // INITIALIZE NOTIFICATION INFO
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

        // BUILD NOTIFCATION
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

        // NOTIFY
        notificationManager.notify(NOTIFICATION_ID, builder.build());
        Log.d("TAG", "Notification is built");
    }
}




