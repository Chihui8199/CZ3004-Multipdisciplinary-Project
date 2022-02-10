package com.example.cx3004;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link RobotStateFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class RobotStateFragment extends Fragment {
    TextView xTextView;
    TextView yTextView;
    TextView directionTextView;

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
    }

    public void setRobotState(int x, int y, String direction){
        xTextView.setText(String.format("X: %d", x));
        yTextView.setText(String.format("Y: %d", y));
        directionTextView.setText(String.format("Direction: %s", direction.toUpperCase()));
        Log.d("ROBOT STATE",
                String.format("Robot state has been set to: x=%d, y=%d, direction=%s",
                        x, y, direction.toUpperCase()));
    }
}