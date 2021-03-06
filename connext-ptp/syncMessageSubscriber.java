
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.ArrayList;
import java.time.Clock;
import java.time.Duration;
import java.time.LocalDate;
import java.lang.Math;

import com.rti.dds.domain.*;
import com.rti.dds.infrastructure.*;
import com.rti.dds.subscription.*;
import com.rti.dds.topic.*;
import com.rti.ndds.config.*;

// ===========================================================================

public class syncMessageSubscriber {

    private static myTimer timer = new myTimer(100);

    // -----------------------------------------------------------------------
    // Public Methods
    // -----------------------------------------------------------------------

    public static void main(String[] args) {
        // --- Get domain ID --- //
        int domainId = 0;
        if (args.length >= 1) {
            domainId = Integer.valueOf(args[0]).intValue();
        }

        // -- Get max loop count; 0 means infinite loop --- //
        int sampleCount = 0;
        if (args.length >= 2) {
            sampleCount = Integer.valueOf(args[1]).intValue();
        }

        /* Uncomment this to turn on additional logging
        Logger.get_instance().set_verbosity_by_category(
            LogCategory.NDDS_CONFIG_LOG_CATEGORY_API,
            LogVerbosity.NDDS_CONFIG_LOG_VERBOSITY_STATUS_ALL);
        */

        // --- Run --- //
        subscriberMain(domainId, sampleCount);
    }

    // -----------------------------------------------------------------------
    // Private Methods
    // -----------------------------------------------------------------------

    // --- Constructors: -----------------------------------------------------

    private syncMessageSubscriber() {
        super();
    }

    // -----------------------------------------------------------------------

    private static void subscriberMain(int domainId, int sampleCount) {

        DomainParticipant participant = null;
        Subscriber subscriber = null;
        Topic topic = null;
        DataReaderListener listener = null;
        syncMessageDataReader reader = null;

        try {
            participant = DomainParticipantFactory.TheParticipantFactory.
            create_participant(
                domainId, DomainParticipantFactory.PARTICIPANT_QOS_DEFAULT,
                null /* listener */, StatusKind.STATUS_MASK_NONE);
            if (participant == null) {
                System.err.println("create_participant error\n");
                return;
            }

            subscriber = participant.create_subscriber(
                DomainParticipant.SUBSCRIBER_QOS_DEFAULT, null /* listener */,
                StatusKind.STATUS_MASK_NONE);
            if (subscriber == null) {
                System.err.println("create_subscriber error\n");
                return;
            }

            String typeName = syncMessageTypeSupport.get_type_name();
            syncMessageTypeSupport.register_type(participant, typeName);

            topic = participant.create_topic(
                "Example syncMessage",
                typeName, DomainParticipant.TOPIC_QOS_DEFAULT,
                null /* listener */, StatusKind.STATUS_MASK_NONE);
            if (topic == null) {
                System.err.println("create_topic error\n");
                return;
            }

            listener = setupListener();

            reader = (syncMessageDataReader)
            subscriber.create_datareader(
                topic, Subscriber.DATAREADER_QOS_DEFAULT, listener,
                StatusKind.STATUS_MASK_ALL);
            if (reader == null) {
                System.err.println("create_datareader error\n");
                return;
            }

            // --- Wait for data --- //

            final long receivePeriodMillis = 10;

            for (int count = 0;
            (sampleCount == 0) || (count < sampleCount);
            ++count) {

                try {
                    // Sleep for a while...
                    Thread.sleep(receivePeriodMillis);
                } catch (InterruptedException ix) {
                    System.err.println("INTERRUPTED");
                    break;
                }
            }
        } finally {

            // --- Shutdown --- //

            if(participant != null) {
                participant.delete_contained_entities();

                DomainParticipantFactory.TheParticipantFactory.
                delete_participant(participant);
            }
        }
    }

    // @ASSIGNMENT HERE ----
    // We add an observer to the messages that allows us to process them
    private static syncMessageListener setupListener() {
      syncMessageListener listener = new syncMessageListener();

      listener.addObserver(syncMessageSubscriber.sync_clock);

      return listener;
    }

    private static SyncComputer syncComp = new SyncComputer();
    private static IMessageObserver sync_clock = (syncMessage message)-> {
      long slaveClock = timer.getClock();
      syncComp.pushSlaveClock(slaveClock);

      long masterClock = Long.valueOf(message.value).longValue();
      syncComp.pushMasterClock(masterClock);
      System.out.println("Pushed clocks  " + (masterClock) + " <> " + (slaveClock));

      int messageType = Integer.valueOf(message.id).intValue();

      //@ASSIGNMENT: If we received a SYNC_MESSAGE,
      // then check if there is a synch difference between our clock and the one received.
      if (messageType == syncMessagePublisher.SYNC_MESSAGE){
        long syncTo = syncComp.computeSyncDiff();
        if (syncTo != 0){
          // @ASSIGNMENT: If there is a difference, then delay our timer with the computed difference.
          // Use a random number to create some oscilation.
          int  rand = (int)(Math.random() * 2);
          timer.setDelay((int)syncTo + rand);
        }
      }
      // @ASSIGNMENT: If we have a delay correction message,
      // Then check the delay and offset and correct our clock accordingly.
      else if (messageType == syncMessagePublisher.DELAY_MESSAGE){
        long delay = syncComp.computeDelay();
        if (delay != 0){
          // @ASSIGNMENT: If there is delay in our system, we need to tune the clock
          // Update it with the computed delay value.
          System.out.println("Got delay in the system...." + delay);
          // The delay is computed from the received clock perspective.
          // i.e. if the delay > 0, then the master clock is behind us, so we need to set the time back.
          timer.updateClock(-delay);
        }
        long offset = syncComp.computeOffset();
        if (offset != 0){
          //@ASSIGNMENT: If there is offset between the clocks, tune our clock with the offset.
          System.out.println("Got offset in the system...." + offset);
          timer.updateClock(offset);
        }
      }
    };

    // -----------------------------------------------------------------------
    // Private Types
    // -----------------------------------------------------------------------

    // =======================================================================

    // Listener for synchronization messages.
    private static class syncMessageListener extends DataReaderAdapter {

        syncMessageSeq _dataSeq = new syncMessageSeq();
        SampleInfoSeq _infoSeq = new SampleInfoSeq();

        private ArrayList<IMessageObserver> observers = new ArrayList<IMessageObserver>();

        public void addObserver(IMessageObserver obs){
          this.observers.add(obs);
        }

        public void on_data_available(DataReader reader) {
            syncMessageDataReader syncMessageReader =
            (syncMessageDataReader)reader;

            try {
                syncMessageReader.take(
                    _dataSeq, _infoSeq,
                    ResourceLimitsQosPolicy.LENGTH_UNLIMITED,
                    SampleStateKind.ANY_SAMPLE_STATE,
                    ViewStateKind.ANY_VIEW_STATE,
                    InstanceStateKind.ANY_INSTANCE_STATE);

                for(int i = 0; i < _dataSeq.size(); ++i) {
                    SampleInfo info = (SampleInfo)_infoSeq.get(i);

                    if (info.valid_data) {
                      syncMessage msg = ((syncMessage)_dataSeq.get(i));

                      // We have a valid message, so call the observers to react
                      for (IMessageObserver obs : observers){
                        obs.react(msg);
                      }
                    }
                }
            } catch (RETCODE_NO_DATA noData) {
                // No data to process
            } finally {
                syncMessageReader.return_loan(_dataSeq, _infoSeq);
            }
        }
    }

    private static interface IMessageObserver{
      void react(syncMessage message);
    }

    // A small class that computes the synchronization differences
    // @ASSIGNMENT This is the PTP synchronization difference computations.
    private static class SyncComputer {
      private long tM1, tM2;
      private long tS1, tS2;

      public SyncComputer(){
        tM1 = tM2 = 0;
        tS1 = tS2 = 0;
      }

      void pushMasterClock(long val){
        tM1 = tM2;
        tM2 = val;
      }

      void pushSlaveClock(long val){
        tS1 = tS2;
        tS2 = val;
      }

      long computeSyncDiff(){
        if(tM1 == 0  || tS1 == 0){
          return 0;
        }

        long masterDiff = tM2 - tM1;
        long slaveDiff = tS2 -tS1;
        if (masterDiff != slaveDiff){
          System.out.println("Found difference between master cycles and slave cycles." + masterDiff + " vs " + slaveDiff);
          int pub_period = syncMessagePublisher.PUBLISH_PERIOD_MS;
          return pub_period/masterDiff;
        }

        long sMDiff1 = tS1 - tM1;
        long sMDiff2 = tS2 - tM2;
        if (sMDiff1 != sMDiff2){
          System.out.println("Found difference between cycle 1 and cycle 2.");
          return sMDiff2 - sMDiff1;
        }
        return 0;
      }

        // Delay = [ (t2-t1) + (t3-t4) ] / 2
      long computeDelay(){
        return ((tS1 - tM1) + (tS2 - tM2)) / 2;
      }

      // Offset = [ (t2-t1) - (t3-t4) ] / 2
      long computeOffset(){
        return ((tS1 - tM1) - (tS2 - tM2)) / 2;
      }
    }
}
