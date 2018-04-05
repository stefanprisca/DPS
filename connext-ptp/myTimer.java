
import javax.swing.Timer;
import java.awt.*;
import java.awt.event.*;

/*
  Custom timing class that keeps an internal clock, which is updated by an external timer.
  Whenever the javax.swing.Timer ticks, our clock variable will be incremented by 1.
  This makes it easier to change and update the clock for synchronization purposes.
*/
public class myTimer {
  private Timer timer;
  private long clock = 0;

  private ActionListener updateClockAction = new ActionListener() {
    public void actionPerformed(ActionEvent e) {
      clock += 1;
    }
  };

  // Creates a new timer with the given delay between ticks.
  // The dealy is used to configure how often this clock ticks.
  public myTimer(int delay){
    timer = new Timer(delay, updateClockAction);
    timer.start();
  }

  public void setDelay(int delay){
    timer.setDelay(delay);
  }

  public long getClock(){
    return clock;
  }

  public void updateClock(long update){
    clock += update;
  }
}
