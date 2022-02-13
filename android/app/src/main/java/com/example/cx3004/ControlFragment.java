package com.example.cx3004;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProviders;

public class ControlFragment extends Fragment {
    // Init
    private static final String ARG_SECTION_NUMBER = "section_number";
    private static final String TAG = "ControlFragment";
    private PageViewModel pageViewModel;

    // Declaration Variable
    ImageButton moveUpImageBtn, moveRightImageBtn, moveLeftImageBtn, moveDownImageBtn;
    double xCoord;
    double yCoord;

    // Fragment Constructor
    public static ControlFragment newInstance(int index) {
        ControlFragment fragment = new ControlFragment();
        Bundle bundle = new Bundle();
        bundle.putInt(ARG_SECTION_NUMBER, index);
        fragment.setArguments(bundle);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        pageViewModel = ViewModelProviders.of(this).get(PageViewModel.class);
        int index = 1;
        if (getArguments() != null) {
            index = getArguments().getInt(ARG_SECTION_NUMBER);
        }
        pageViewModel.setIndex(index);
    }

    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {
        // inflate
        View root = inflater.inflate(R.layout.fragment_controls, container, false);

        // variable initialization
        moveUpImageBtn = root.findViewById(R.id.upImageBtn);
        moveRightImageBtn = root.findViewById(R.id.rightImageBtn);
        moveLeftImageBtn = root.findViewById(R.id.leftImageBtn);
        moveDownImageBtn = root.findViewById(R.id.downImageBtn);


        // Button Listener
        //TODO Need to check if it's ok to create static var like this
        moveUpImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                xCoord = ((MainActivity) getActivity()).getXCoord();
                yCoord = ((MainActivity) getActivity()).getYCoord();
                ((MainActivity) getActivity()).moveRobot(xCoord, yCoord + 1, "up");

                // TODO Check with RPI what command to send
                ((MainActivity) getActivity()).remoteSendMsg("REMOTE, UP, 1");
            }
        });

        moveRightImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                xCoord = ((MainActivity) getActivity()).getXCoord();
                yCoord = ((MainActivity) getActivity()).getYCoord();
                ((MainActivity) getActivity()).moveRobot(xCoord + 1, yCoord, "right");
                ((MainActivity) getActivity()).remoteSendMsg("REMOTE, RIGHT, 1");
            }
        });

        moveLeftImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                xCoord = ((MainActivity) getActivity()).getXCoord();
                yCoord = ((MainActivity) getActivity()).getYCoord();
                ((MainActivity) getActivity()).moveRobot(xCoord - 1, yCoord, "left");
                ((MainActivity) getActivity()).remoteSendMsg("REMOTE, LEFT, 1");
            }
        });

        moveDownImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                xCoord = ((MainActivity) getActivity()).getXCoord();
                yCoord = ((MainActivity) getActivity()).getYCoord();
                ((MainActivity) getActivity()).moveRobot(xCoord, yCoord - 1, "down");
                ((MainActivity) getActivity()).remoteSendMsg("REMOTE, DOWN, 1");
            }
        });

        return root;
    }


}
