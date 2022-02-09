package com.example.cx3004.customViews;

import android.content.ClipData;
import android.content.ClipDescription;
import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import androidx.annotation.Nullable;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.content.ContextCompat;

import com.example.cx3004.R;

/** A view class for obstacles.
* This view should only be used within the SquareGridView
*/
public class ObstacleView extends androidx.appcompat.widget.AppCompatTextView {

    public int id;
    private int gridInterval;
    private int x;
    private int y;
    public String imageFace = "";
    public boolean setOnMap = false; // true when obstacle has been placed on map

    private float initX;
    private float initY;

    public ObstacleView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);

        TypedArray a = context.getTheme().obtainStyledAttributes(
                attrs,
                R.styleable.ObstacleView,
                0, 0);
        try {
            id = Integer.parseInt(getText().toString());
            setTextSize(getResources().getDimensionPixelSize(R.dimen.small_text_size));
            setTextColor(Color.WHITE);
            setBackgroundResource(R.color.black);
            setGravity(Gravity.CENTER);
        } finally {
            a.recycle();
        }

        setOnLongClickListener(new OnLongClickListener() {
            @Override
            public boolean onLongClick(View view) {
                DragShadowBuilder dragShadowBuilder = new DragShadowBuilder(view);
                view.startDragAndDrop(null, dragShadowBuilder, ObstacleView.this, 0);
                return true;
            }
        });
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        Paint borderPaint = new Paint();
        borderPaint.setColor(Color.RED);
        borderPaint.setStrokeWidth(10);

        switch (imageFace){
            case "up":
                canvas.drawLine(0, 0, gridInterval, 0, borderPaint);
                break;
            case "down":
                canvas.drawLine(0, gridInterval, gridInterval, gridInterval, borderPaint);
                break;
            case "left":
                canvas.drawLine(0, 0, 0, gridInterval, borderPaint);
                break;
            case "right":
                canvas.drawLine(gridInterval, 0, gridInterval, gridInterval, borderPaint);
                break;
            default:
                break;
        }
    }

    @Override
    public String toString() {
        // for debugging purposes
        return "ObstacleView{" +
                "id=" + id +
                ", gridInterval=" + gridInterval +
                ", x=" + x +
                ", y=" + y +
                ", imageFace='" + imageFace + '\'' +
                '}';
    }

    public void move(float xCoord, float yCoord){
        // snaps obstacle to the grid

        // store initial coordinates if obstacle has not been placed on map
        if (!setOnMap){
            initX = getX();
            initY = getY();
        }

        x = (int) Math.floor(xCoord / gridInterval);

        // the screen y coordinates start from the top,
        // the grid y coordinates starts from the bottom
        int screenY = (int) Math.floor(yCoord / gridInterval);
        y = 19 - screenY;

        setX(x * gridInterval);
        setY(screenY * gridInterval);
    }

    public void reset(){
        // reset attributes
        x = -1;
        y = -1;
        imageFace = "";
        setOnMap = false;

        // reset position
        setX(initX);
        setY(initY);

        // redraw
        invalidate();
    }

    // called after layout
    public void setGridInterval(int gridInterval){
        this.gridInterval = gridInterval;

        // resize view
        ViewGroup.LayoutParams params = getLayoutParams();
        params.height = gridInterval;
        params.width = gridInterval;
        setLayoutParams(params);
    }

    public void setImageFace(String imageFace) {
        this.imageFace = imageFace;
        invalidate(); // redraw obstacle with new image face border
    }

    public void setImage(int imageID){
        setText("");
        String imageResourceID = String.format("obstacle_image_%d", imageID);
        int imageResourceIntID = getResources().getIdentifier(imageResourceID, "drawable", getContext().getPackageName());
        if (imageResourceIntID != 0) setBackgroundResource(imageResourceIntID);
    }

    public String getMessage(){
        return String.format("Obstacle %d (%d, %d, %s)", id, x, y, imageFace);
    }
}
