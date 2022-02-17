package com.example.cx3004;

import android.app.Activity;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.DragEvent;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ImageButton;
import android.widget.PopupWindow;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.viewpager.widget.ViewPager;

import com.example.cx3004.customViews.ObstacleView;
import com.example.cx3004.customViews.RobotView;
import com.example.cx3004.customViews.SquareGridView;
import com.google.android.material.tabs.TabLayout;

import org.json.JSONArray;
import org.json.JSONException;

import java.nio.charset.Charset;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    ObstacleView[] obstacleViews;
    // flags are set when the corresponding obstacle is placed on the grid
    boolean[] obstacleFlags = new boolean[]{false, false, false, false, false};
    public static RobotView robotView;

    static SectionsPagerAdapter sectionsPagerAdapter;

    // Declaration Variables
    private static SharedPreferences sharedPreferences;
    private static SharedPreferences.Editor editor;
    private static Context context;
    BluetoothConnectionService mBluetoothConnection;
    BluetoothDevice mBTDevice;
    private static UUID myUUID;

    private static final String TAG = "MAIN ACTIVITY";
    private static final String ROBOTTAG = "ROBOT";
    private static final String GRIDTAG = "GRID";
    private static final String BTTAG = "BLUETOOTH";

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // Initialization
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        sectionsPagerAdapter = new SectionsPagerAdapter(this, getSupportFragmentManager());
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

        // instantiate views
        // instantiate robot view
        robotView = (RobotView) findViewById(R.id.robot);
        //instantiate obstacle view
        int[] obstacleIDs = new int[]{
                R.id.obstacle1,
                R.id.obstacle2,
                R.id.obstacle3,
                R.id.obstacle4,
                R.id.obstacle5
        };
        obstacleViews = new ObstacleView[obstacleIDs.length];
        for (int i = 0; i < obstacleIDs.length; i++)
            obstacleViews[i] = findViewById(obstacleIDs[i]);


        // set on drag listener for grid map
        SquareGridView gridMap = (SquareGridView) findViewById(R.id.grid_map);
        gridMap.setOnDragListener(new View.OnDragListener() {
            @Override
            public boolean onDrag(View view, DragEvent dragEvent) {
                switch (dragEvent.getAction()) {
                    case DragEvent.ACTION_DROP:
                        ObstacleView droppedObstacle = (ObstacleView) dragEvent.getLocalState();
                        Log.d(GRIDTAG, String.format("Obstacle %d was dropped on the map.",
                                        droppedObstacle.getObstacleId()));
                        droppedObstacle.move(dragEvent.getX(), dragEvent.getY());
                        Log.d(GRIDTAG,
                                String.format("Obstacle %d was moved to (%d, %d) on the map.",
                                        droppedObstacle.getObstacleId(),
                                        droppedObstacle.getGridX(),
                                        droppedObstacle.getGridY()));
                        // get obstacle image face using popup
                        showImageFacePopup(droppedObstacle);
                        break;
                    case DragEvent.ACTION_DRAG_ENDED:
                        if (!dragEvent.getResult()) {
                            droppedObstacle = (ObstacleView) dragEvent.getLocalState();
                            Log.d(GRIDTAG,
                                    String.format("Obstacle %d was dropped outside of the map.",
                                            droppedObstacle.getObstacleId()));
                            droppedObstacle.reset();
                            Log.d(GRIDTAG,
                                    String.format("Obstacle %d was reset.",
                                            droppedObstacle.getObstacleId()));
                        }
                        break;
                }
                return true;
            }
        });

        // actual width and height of views is only measured after layout
        // hence, resize obstacles and set robot after layout is complete
        // grid boxes and obstacles should be same size
        View rootView = (View) findViewById(R.id.main_layout);
        rootView.post(new Runnable() {
            @Override
            public void run() {
                for (ObstacleView obstacle : obstacleViews) {
                    obstacle.setGridInterval(gridMap.gridInterval);
                    Log.d(GRIDTAG,
                            String.format("Obstacle %d has been resized to match grid boxes.",
                                    obstacle.getObstacleId()));
                }
                robotView.setGridInterval(gridMap.gridInterval);
                robotView.bringToFront();
                Log.d(ROBOTTAG,
                        "Robot has been resized to match grid boxes " +
                                "and positioned at bottom-left corner of map.");
            }
        });
    }

    private static void showLog(String message) {
        Log.d(TAG, message);
    }
    
    public static void moveRobot(double xCoord, double yCoord, String direction) {
        // if coordinates are out of bounds, break out of function and not move the robot
        if (!robotView.checkBoundary(xCoord, yCoord)) return;
        robotView.move(xCoord, yCoord, direction);
        Log.d(ROBOTTAG,
                String.format("Robot has been moved to (%f, %f) on the map and is facing %s.",
                        xCoord, yCoord, direction));
        refreshRobotState(xCoord, yCoord, direction);
    }

    private static void refreshRobotState(double xCoord, double yCoord, String direction) {
        sectionsPagerAdapter.robotStateFragment.setRobotState(xCoord, yCoord, direction);
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
                    Log.d(GRIDTAG,
                            String.format("Image face for obstacle %d has been set to '%s'.",
                                    obstacle.getObstacleId(), face));
                    obstacle.setOnMap = true;
                    popupWindow.dismiss();
                }
            });
        }

        popupWindow.setOnDismissListener(new PopupWindow.OnDismissListener() {
            @Override
            public void onDismiss() {
                // check if all obstacles have been placed on map
                // if an obstacle has not been set, break out of function
                for (ObstacleView obstacle : obstacleViews)
                    if (!obstacle.setOnMap) return;
                Log.d(GRIDTAG, "All obstacles have been placed on map.");

                // if all obstacles have been set, send obstacle coordinate messages
                for (ObstacleView obstacle : obstacleViews) {
                    remoteSendMsg(obstacle.getMessage());
                    Log.d(BTTAG,
                            String.format("Obstacle message has been sent for obstacle %d",
                                    obstacle.getObstacleId()));
                }
            }
        });


    }

    //Bluetooth Stuff
    public static void sharedPreferences() {
        sharedPreferences = MainActivity.getSharedPreferences(MainActivity.context);
        editor = sharedPreferences.edit();
    }

    public static void refreshMessageReceived() {
        CommsFragment.getMessageReceivedTextView().setText(sharedPreferences.getString("message", ""));
    }

    private static SharedPreferences getSharedPreferences(Context context) {
        return context.getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
    }

    // Broadcast Receiver 5:  for Bluetooth Connection Status
    private BroadcastReceiver btConnectionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            BluetoothDevice mDevice = intent.getParcelableExtra("Device");
            String status = intent.getStringExtra("Status");
            sharedPreferences();
            if (status.equals("connected")) {
                Log.d(BTTAG, "mBroadcastReceiver5: Device now connected to " + mDevice.getName());
                Toast.makeText(MainActivity.this, "Device now connected to " + mDevice.getName(), Toast.LENGTH_SHORT).show();
                editor.putString("connStatus", "Connected to " + mDevice.getName());

            } else if (status.equals("disconnected")) {
                Log.d(BTTAG, "mBroadcastReceiver5: Disconnected from " + mDevice.getName());
                Toast.makeText(MainActivity.this, "Disconnected from " + mDevice.getName(), Toast.LENGTH_SHORT).show();
                editor.putString("connStatus", "Disconnected");
            }
            editor.commit();
        }
    };

    BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String message = intent.getStringExtra("receivedMessage");
            // Read message to parse as commands
            parseCommands(message);
            showLog("receivedMessage: message --- " + message);
            sharedPreferences();
            String receivedText = sharedPreferences.getString("message", "") + "\n" + message;
            editor.putString("message", receivedText);
            editor.commit();
            refreshMessageReceived();
        }
    };

    private void parseCommands(String receivedText) {
        //TODO to update timing commands
        // Process Algo Msg which is a list of list
        if (receivedText.contains("[[")) {
            try {
                parseAlgoMsg(receivedText);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        } else {
            Log.d("NO COMMANDS ACTIVATED", "NIL");
        }
    }

    private void parseAlgoMsg(String receivedText) throws JSONException {
        JSONArray jsonArr = new JSONArray(receivedText);
        // process robot current x,y,direction
        parseCoordsCmd(jsonArr.getJSONArray(0));
        // update obstacle with target image
        parseObstacleTargets(jsonArr);
    }

    private static void parseCoordsCmd(JSONArray coordsArray) throws JSONException {
        // retrieves x,y,angle from algo msg
        double xCoord = coordsArray.getDouble(0);
        double yCoord = coordsArray.getDouble(1);
        double angleRad = coordsArray.getDouble(2);

        // process angle into android application readable directions
        String direction = "up";
        double angleDeg = angleRad / (2 * Math.PI) * 360;
        if ((0 <= angleDeg & angleDeg <= 45) | (315 < angleDeg & angleDeg < 360))
            direction = "left";
        else if (45 < angleDeg & angleDeg <= 135) direction = "up";
        else if (135 < angleDeg & angleDeg <= 255) direction = "right";
        else if (255 < angleDeg & angleDeg <= 315) direction = "down";
        else Log.d("COMMAND", "Unknown direction passed. Direction set to 'up' by default");

        // call method to update ROBOT, X, Y, direction
        // moves robot and sets fragment to correct axis
        moveRobot(xCoord, yCoord, direction);
        Log.d(TAG, String.format("Robot Status set as: X: %f Y: %f Z %s", xCoord, yCoord, direction));
    }

    private void parseObstacleTargets(JSONArray entireArrayMsg) {
        // iterate from 1 - end of list to get targets
        int obstacleNo;
        int targetID;
        for (int i = 1, size = entireArrayMsg.length(); i <= size; i++) {
            obstacleNo = i;
            try {
                targetID = entireArrayMsg.getJSONArray(i).getInt(0);
                // update the image face
                if (targetID != -1) {
                    // call method to update Obstacle Number, ID
                    obstacleViews[obstacleNo - 1].setImage(targetID);
                    Log.d("OBSTACLE", String.format("Obstacle %d's image has been set to image ID %d.", obstacleNo, targetID));
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

// TODO: remove commented portion if all is well

//    private void parseCommands(String receivedText) {
//        Log.d(TAG, "Testing" + receivedText);
//        try {
//            if (receivedText.contains(",")) {
//                String[] stringSplit = receivedText.split(",");
//                String command = stringSplit[0];
//                if (command.equals("ROBOT")) {
//                    double xCoord = Double.parseDouble(stringSplit[1]);
//                    double yCoord = Double.parseDouble(stringSplit[2]);
//                    // process direction
//                    // angle is sent in radians, convert to degrees
//                    double angle = Double.parseDouble(stringSplit[3]) / (2 * Math.PI) * 360;
//                    String direction = "up";
//                    if ((0 <= angle & angle <= 45) | (315 < angle & angle < 360))
//                        direction = "left";
//                    else if (45 < angle & angle <= 135) direction = "up";
//                    else if (135 < angle & angle <= 255) direction = "right";
//                    else if (255 < angle & angle <= 315) direction = "down";
//                    else
//                        Log.d("COMMAND", "Unknown direction passed. Direction set to 'up' by default");
//                    Log.d("COMMAND ACTIVATED ", command + " " + xCoord + " " + yCoord + " " + direction);
//                    // call method to update ROBOT, X, Y, direction
//                    // moves robot and sets fragment to correct axis
//                    moveRobot(xCoord, yCoord, direction);
//                } else if (command.equals("TARGET")) {
//                    int obstacleNo = Integer.parseInt(stringSplit[1]);
//                    int targetID = Integer.parseInt(stringSplit[2]);
//                    Log.d("COMMAND ACTIVATED ", command + " " + obstacleNo + " " + targetID);
//                    // call method to update Obstacle Number, ID
//                    obstacleViews[obstacleNo - 1].setImage(targetID);
//                    Log.d("OBSTACLE",
//                            String.format("Obstacle %d's image has been set to image ID %d.",
//                                    obstacleNo, targetID));
//                } else if (command.equals("TIMING")) {
//                    String timing = stringSplit[1];
//                    sectionsPagerAdapter.fastestCarFragment.setTiming(timing);
//                } else {
//                    Log.d("NO COMMANDS ACTIVATED", "NIL");
//                }
//            }
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//    }

    // Send message to bluetooth remotely
    public static void remoteSendMsg(String message) {
        showLog("Entering printMessage: " + message);
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
            LocalBroadcastManager.getInstance(this).unregisterReceiver(btConnectionReceiver);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(btConnectionReceiver);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        try {
            IntentFilter filter2 = new IntentFilter("ConnectionStatus");
            LocalBroadcastManager.getInstance(this).registerReceiver(btConnectionReceiver, filter2);
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
}