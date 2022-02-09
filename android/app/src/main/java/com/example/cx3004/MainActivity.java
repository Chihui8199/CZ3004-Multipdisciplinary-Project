package com.example.cx3004;

import android.app.Activity;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.media.Image;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.DragEvent;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewTreeObserver;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.viewpager.widget.ViewPager;

import com.example.cx3004.customViews.ObstacleView;
import com.example.cx3004.customViews.RobotView;
import com.example.cx3004.customViews.SquareGridView;
import com.google.android.material.tabs.TabLayout;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.Charset;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    int[] obstacleIDs = new int[]{
            R.id.obstacle1,
            R.id.obstacle2,
            R.id.obstacle3,
            R.id.obstacle4,
            R.id.obstacle5
    };
    // flags are set when the corresponding obstacle is placed on the grid
    boolean[] obstacleFlags = new boolean[]{false, false, false, false, false};
    RobotView robotView;

    // Declaration Variables
    private static SharedPreferences sharedPreferences;
    private static SharedPreferences.Editor editor;
    private static Context context;

    BluetoothConnectionService mBluetoothConnection;
    BluetoothDevice mBTDevice;
    private static UUID myUUID;
    ProgressDialog myDialog;

    private static final String TAG = "Main Activity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // Initialization
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        SectionsPagerAdapter sectionsPagerAdapter = new SectionsPagerAdapter(this, getSupportFragmentManager());
        ViewPager viewPager = findViewById(R.id.view_pager);
        viewPager.setAdapter(sectionsPagerAdapter);
        viewPager.setOffscreenPageLimit(9999);
        TabLayout tabs = findViewById(R.id.tabs);
        tabs.setupWithViewPager(viewPager);
        LocalBroadcastManager.getInstance(this).registerReceiver(messageReceiver, new IntentFilter("incomingMessage"));

        // Set up sharedPreferences
        MainActivity.context = getApplicationContext();
        this.sharedPreferences();
        editor.putString("message", "");
        //editor.putString("direction", "None");
        editor.putString("connStatus", "Disconnected");
        editor.commit();


        // Toolbar
        ImageButton bluetoothButton = (ImageButton) findViewById(R.id.bluetoothButton);
        bluetoothButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent popup = new Intent(MainActivity.this, BluetoothPairingPage.class);
                startActivity(popup);
            }
        });

        myDialog = new ProgressDialog(MainActivity.this);
        myDialog.setMessage("Waiting for other device to reconnect...");
        myDialog.setCancelable(false);
        myDialog.setButton(DialogInterface.BUTTON_NEGATIVE, "Cancel", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.dismiss();
            }
        });

        // set on drag listener for grid map
        SquareGridView gridMap = (SquareGridView) findViewById(R.id.grid_map);
        gridMap.setOnDragListener(new View.OnDragListener() {
            @Override
            public boolean onDrag(View view, DragEvent dragEvent) {
                if (dragEvent.getAction() == DragEvent.ACTION_DROP) {
                    // get obstacle view
                    CharSequence id_data = dragEvent.getClipData().getItemAt(0).getText();
                    int id = Integer.parseInt(id_data.toString());
                    ObstacleView obstacle = (ObstacleView) findViewById(id);

                    // move obstacle
                    obstacle.move(dragEvent.getX(), dragEvent.getY());

                    // get obstacle image face using popup
                    showImageFacePopup(obstacle);

                    // set obstacle flag
                    obstacleFlags[obstacle.id-1] = true;

                    // check if all obstacle flags have been set


                }
                return true;
            }
        });

        // instantiate robot view
        robotView = (RobotView) findViewById(R.id.robot);

        // actual width and height of views is only measured after layout
        // hence, resize obstacles and set robot after layout is complete
        // grid boxes and obstacles should be same size
        View rootView = (View) findViewById(R.id.main_layout);
        rootView.post(new Runnable() {
            @Override
            public void run() {
                for (int id : obstacleIDs) {
                    ObstacleView obstacle = (ObstacleView) findViewById(id);
                    obstacle.setGridInterval(gridMap.gridInterval);

                }
                robotView.setGridInterval(gridMap.gridInterval);
                robotView.bringToFront();
            }
        });
    }

    public static void sharedPreferences() {
        sharedPreferences = MainActivity.getSharedPreferences(MainActivity.context);
        editor = sharedPreferences.edit();
    }

    // Send message to bluetooth
    public static void printMessage(String message) {
        showLog("Entering printMessage");
        editor = sharedPreferences.edit();

        if (BluetoothConnectionService.BluetoothConnectionStatus == true) {
            byte[] bytes = message.getBytes(Charset.defaultCharset());
            BluetoothConnectionService.write(bytes);
        }
        showLog(message);
        editor.putString("message", CommsFragment.getMessageReceivedTextView().getText() + "\n" + message);
        editor.commit();
        refreshMessageReceived();
        showLog("Exiting printMessage");
    }

    public static void printMessage(String name, int x, int y) throws JSONException {
        showLog("Entering printMessage");
        sharedPreferences();

        JSONObject jsonObject = new JSONObject();
        String message;

        switch (name) {
//            case "starting":
            case "waypoint":
                jsonObject.put(name, name);
                jsonObject.put("x", x);
                jsonObject.put("y", y);
                message = name + " (" + x + "," + y + ")";
                break;
            default:
                message = "Unexpected default for printMessage: " + name;
                break;
        }
        editor.putString("message", CommsFragment.getMessageReceivedTextView().getText() + "\n" + message);
        editor.commit();
        if (BluetoothConnectionService.BluetoothConnectionStatus == true) {
            byte[] bytes = message.getBytes(Charset.defaultCharset());
            BluetoothConnectionService.write(bytes);
        }
        showLog("Exiting printMessage");
    }

    public static void refreshMessageReceived() {
        CommsFragment.getMessageReceivedTextView().setText(sharedPreferences.getString("message", ""));
    }

    public static void receiveMessage(String message) {
        showLog("Entering receiveMessage");
        sharedPreferences();
        editor.putString("message", sharedPreferences.getString("message", "") + "\n" + message);
        editor.commit();
        showLog("Exiting receiveMessage");
    }

    private static void showLog(String message) {
        Log.d(TAG, message);
    }

    private static SharedPreferences getSharedPreferences(Context context) {
        return context.getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
    }

    private BroadcastReceiver mBroadcastReceiver5 = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            BluetoothDevice mDevice = intent.getParcelableExtra("Device");
            String status = intent.getStringExtra("Status");
            sharedPreferences();

            if (status.equals("connected")) {
                try {
                    myDialog.dismiss();
                } catch (NullPointerException e) {
                    e.printStackTrace();
                }

                Log.d(TAG, "mBroadcastReceiver5: Device now connected to " + mDevice.getName());
                Toast.makeText(MainActivity.this, "Device now connected to " + mDevice.getName(), Toast.LENGTH_LONG).show();
                editor.putString("connStatus", "Connected to " + mDevice.getName());

            } else if (status.equals("disconnected")) {
                Log.d(TAG, "mBroadcastReceiver5: Disconnected from " + mDevice.getName());
                Toast.makeText(MainActivity.this, "Disconnected from " + mDevice.getName(), Toast.LENGTH_LONG).show();


                editor.putString("connStatus", "Disconnected");


                myDialog.show();
            }
            editor.commit();
        }
    };

    BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String message = intent.getStringExtra("receivedMessage");
            showLog("receivedMessage: message --- " + message);
            // write specific commands here
            sharedPreferences();
            String receivedText = sharedPreferences.getString("message", "") + "\n" + message;
            editor.putString("message", receivedText);
            editor.commit();
            refreshMessageReceived();
        }
    };

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case 1:
                if (resultCode == Activity.RESULT_OK) {
                    mBTDevice = (BluetoothDevice) data.getExtras().getParcelable("mBTDevice");
                    myUUID = (UUID) data.getSerializableExtra("myUUID");
                }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(messageReceiver);
            LocalBroadcastManager.getInstance(this).unregisterReceiver(mBroadcastReceiver5);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(mBroadcastReceiver5);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        try {
            IntentFilter filter2 = new IntentFilter("ConnectionStatus");
            LocalBroadcastManager.getInstance(this).registerReceiver(mBroadcastReceiver5, filter2);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        showLog("Entering onSaveInstanceState");
        super.onSaveInstanceState(outState);

        outState.putString(TAG, "onSaveInstanceState");
        showLog("Exiting onSaveInstanceState");
    }

    private void showImageFacePopup(ObstacleView obstacle) {

        final PopupWindow popupWindow = new PopupWindow(this);

        // inflate layout
        LayoutInflater inflater = (LayoutInflater) getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        View view = inflater.inflate(R.layout.image_face_popup, null);

        popupWindow.setContentView(view);
        popupWindow.showAtLocation(view, Gravity.CENTER, 0, 0);

        // set buttons
        int[] buttonIDs = new int[]{
                R.id.up_button, R.id.down_button,
                R.id.left_button, R.id.right_button
        };
        String[] faces = new String[]{"up", "down", "left", "right"};
        for (int i = 0; i < buttonIDs.length; i++) {
            View button = view.findViewById(buttonIDs[i]);
            String face = faces[i];
            button.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    obstacle.setImageFace(face);

                    System.out.println(obstacle);

                    popupWindow.dismiss();
                }
            });
        }

    }
}