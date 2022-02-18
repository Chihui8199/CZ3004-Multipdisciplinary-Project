package com.example.cx3004;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.text.DecimalFormat;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link RobotStateFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class RobotStateFragment extends Fragment {
    TextView xTextView;
    TextView yTextView;
    TextView directionTextView;
    TextView statusTextView;

    public static RobotStateFragment newInstance() {
        RobotStateFragment fragment = new RobotStateFragment();
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_robot_state, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        xTextView = (TextView) getView().findViewById(R.id.robot_x_state);
        yTextView = (TextView) getView().findViewById(R.id.robot_y_state);
        directionTextView = (TextView) getView().findViewById(R.id.robot_direction_state);
        statusTextView = (TextView) getView().findViewById(R.id.robot_status);
    }

    public void setRobotState(double x, double y, String direction){
        setRobotState(x, y, direction, null);
    }

    public void setRobotState(double x, double y, String direction, String status) {
        // remove trailing zeros from coords
        DecimalFormat coordFormat = new DecimalFormat("0.#");
        String xStr = String.format("X: %s", coordFormat.format(x));
        String yStr = String.format("Y: %s", coordFormat.format(y));
        String directionStr = String.format("Direction: %s", direction.toUpperCase());

        // set text in text views
        xTextView.setText(xStr);
        yTextView.setText(yStr);
        directionTextView.setText(directionStr);
        if (status != null) statusTextView.setText(String.format("Status: %s", status));

        Log.d("ROBOT STATE",
                String.format("Robot state has been set to: %s, %s, %s",
                        xStr, yStr, directionStr));
    }
}