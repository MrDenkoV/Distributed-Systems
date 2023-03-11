package Z2;

import akka.actor.typed.ActorRef;
import akka.actor.typed.Behavior;
import akka.actor.typed.javadsl.AbstractBehavior;
import akka.actor.typed.javadsl.ActorContext;
import akka.actor.typed.javadsl.Behaviors;
import akka.actor.typed.javadsl.Receive;
import akka.actor.typed.receptionist.Receptionist;

import java.util.LinkedList;
import java.util.List;

public class ActorTextService extends AbstractBehavior<ActorTextService.Command>  {

    // --- messages
    interface Command {}

    // TODO: new message type implementing Command, with Receptionist.Listing field

    public static class Request implements Command {
        final String text;

        public Request(String text) {
            this.text = text;
        }
    }


    // --- constructor and create
    // TODO: field for message adapter
    private List<ActorRef<String>> workers = new LinkedList<>();

    public ActorTextService(ActorContext<ActorTextService.Command> context) {
        super(context);

        // TODO: create message adapter

        // TODO: subscribe to receptionist (with message adapter)
    }

    public static Behavior<Command> create() {
        return Behaviors.setup(ActorTextService::new);
    }

    // --- define message handlers
    @Override
    public Receive<Command> createReceive() {

        System.out.println("creating receive for text service");

        return newReceiveBuilder()
                .onMessage(Request.class, this::onRequest)
                // TODO: handle the new type of message
                .build();
    }

    private Behavior<Command> onRequest(Request msg) {
        System.out.println("request: " + msg.text);
        for (ActorRef<String> worker : workers) {
            System.out.println("sending to worker: " + worker);
            worker.tell(msg.text);
        }
        return this;
    }

    // TODO: handle the new type of message

}
