
import javax.swing.Timer;
import java.awt.*;
import java.awt.event.*;

public class myTimer {
  private Timer timer;
  private long clock = 0;

  private ActionListener updateClockAction = new ActionListener() {
    public void actionPerformed(ActionEvent e) {
      clock += 1;
    }
  };

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
}
