package com.example.cx3004.customViews;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.ViewGroup;

import androidx.annotation.Nullable;

import com.example.cx3004.R;

public class RobotView extends androidx.appcompat.widget.AppCompatTextView {
    private int gridInterval;
    // coordinates are measured from center of the robot
    public double gridX;
    public double gridY;
    public String direction;
    private final int SIZE_SCALE = 3; // no of boxes the robot should take up
    private final double MIN_COORD = 1;
    private final double MAX_COORD = 18;

    public RobotView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);

        setBackgroundResource(R.color.faint_orange);
        setGravity(Gravity.CENTER);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // draw triangle arrow
        int height = getHeight();
        int width = getWidth();
        int top = (int) 0.2 * height;
        int bottom = (int) 0.5 * height;
        int left = (int) 0.4 * width;
        int right = (int) 0.6 * width;
        Drawable triangleArrow = getResources().getDrawable(R.drawable.triangle_arrow_up, null);
        triangleArrow.setBounds(0, 0, getWidth(), getHeight());
        triangleArrow.draw(canvas);
    }

    public void setGridInterval(int gridInterval) {
        this.gridInterval = gridInterval;

        // resize view
        ViewGroup.LayoutParams params = getLayoutParams();
        params.height = SIZE_SCALE * gridInterval;
        params.width = SIZE_SCALE * gridInterval;
        setLayoutParams(params);

        // set robot at 0, 0
        //setX(0);
        //setY(0);
        move(MIN_COORD, MIN_COORD, "up");
    }


    public void move(double x, double y, String direction){
        // set direction
        switch (direction) {
            case "left":
                setRotation(-90);
                this.direction = direction;
                break;
            case "right":
                setRotation(90);
                this.direction = direction;
                break;
            case "down":
                setRotation(180);
                this.direction = direction;
                break;
            case "up":
                setRotation(0);
                this.direction = direction;
                break;
        }

        // set coordinates
        setX((float) ((x - MIN_COORD) * gridInterval));
        setY((float) ((19 - y - MIN_COORD) * gridInterval));
        this.gridX = x;
        this.gridY = y;
    }

    public boolean checkBoundary(double x, double y){
        return (MIN_COORD<= x & x <= MAX_COORD) & (MIN_COORD <= y & y <= MAX_COORD);
    }

    public double getGridX(){
        return gridX;
    }

    public double getGridY(){
        return gridY;
    }

    public String getRobotDirection(){
        return direction;
    }

    public double getInitCoord(){ return MIN_COORD; }
}
