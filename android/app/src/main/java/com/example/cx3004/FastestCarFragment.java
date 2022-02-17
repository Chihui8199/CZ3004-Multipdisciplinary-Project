package com.example.cx3004;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProviders;

/**
 * A placeholder fragment containing a simple view.
 */
public class FastestCarFragment extends Fragment {

    private static final String ARG_SECTION_NUMBER = "section_number";
    private static final String TAG = "FastestCarFragment";

    private PageViewModel pageViewModel;

    public static FastestCarFragment newInstance(int index) {
        FastestCarFragment fragment = new FastestCarFragment();
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
        View root = inflater.inflate(R.layout.fragment_fastest_car, container, false);

        Button startButton = root.findViewById(R.id.startBtn);
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // todo check with rpi what start command is
                ((MainActivity) getActivity()).remoteSendMsg("FASTEST");
            }
        });

        return root;
    }

    public void setTiming(String timing) {
        TextView timingText = (TextView) getView().findViewById(R.id.timing);
        timingText.setText(String.format("Timing: %s", timing));
    }

}