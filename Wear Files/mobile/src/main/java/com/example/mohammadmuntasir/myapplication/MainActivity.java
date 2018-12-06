package com.example.mohammadmuntasir.myapplication;

import android.net.wifi.WifiManager;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Enumeration;

public class MainActivity extends AppCompatActivity {

    private TextView mTextView;
    private ServerSocket serverSocket;
    Handler updateConversationHandler;
    Thread serverThread = null;
    TextView message;

    public static final int port = 1095;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mTextView = (TextView) findViewById(R.id.text);
        // Enables Always-on
        //setAmbientEnabled();
        message = (TextView) findViewById(R.id.message);
        updateConversationHandler = new Handler();

        //this.serverThread = new Thread(new ServerThread());
        //message.setText("we will try sockets REAL soon!");
        //message.setText("");
        message.setText("Hi!");
        WifiManager wm = (WifiManager) getSystemService(WIFI_SERVICE);
        String str = "hi";
        try {
            for (Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces();
                 en.hasMoreElements();) {
                NetworkInterface intf = en.nextElement();
                for (Enumeration<InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements();) {
                    InetAddress inetAddress = enumIpAddr.nextElement();
                    if (!inetAddress.isLoopbackAddress()) {
                        str = inetAddress.getHostAddress().toString();
                    }
                }
            }
        } catch (Exception ex) {
            // nothing
        }
        message.setText(str);
        this.serverThread = new Thread(new ServerThread());
        this.serverThread.start();
        //message.setText("The end");
    }

    @Override
    protected void onStop() {
        super.onStop();
        try {
            message.setText("This happened");
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    class ServerThread implements Runnable {
        public ServerThread(){
            message.setText("created");
        }
        public void run() {
            Socket socket = null;
            try {
                serverSocket = new ServerSocket(port);
                message.setText("successfully created");
            } catch (IOException e) {
                e.printStackTrace();
            }
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    message.setText("Waiiting...");
                    socket = serverSocket.accept();
                    message.setText("skipped");
                    CommunicationThread commThread = new CommunicationThread(socket);
                    new Thread(commThread).start();

                } catch (IOException e) {
                    e.printStackTrace();
                    message.setText("error");
                }
            }
        }

    }


    class CommunicationThread implements Runnable {
        private Socket clientSocket;
        private BufferedReader input;
        public CommunicationThread(Socket clientSocket) {
            this.clientSocket = clientSocket;
            try {
                this.input = new BufferedReader(new InputStreamReader(this.clientSocket.getInputStream()));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        public void run() {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    String read = input.readLine();
                    updateConversationHandler.post(new updateUIThread(read));
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

    }

    class updateUIThread implements Runnable {
        private String msg;

        public updateUIThread(String str) {
            this.msg = str;
        }

        @Override
        public void run() {
            message.setText(message.getText().toString()+"Client Says: "+ msg + "\n");
        }
    }


}
