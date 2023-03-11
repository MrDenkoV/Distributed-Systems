package HelloWorld;

import akka.actor.typed.Behavior;
import akka.actor.typed.javadsl.AbstractBehavior;
import akka.actor.typed.javadsl.ActorContext;
import akka.actor.typed.javadsl.Behaviors;
import akka.actor.typed.javadsl.Receive;

public class HelloActor extends AbstractBehavior<String> {

    // --- constructor and create
    public HelloActor(ActorContext<String> context) {
        super(context);
    }

    public static Behavior<String> create() {
        return Behaviors.setup(HelloActor::new);
    }

    // --- define message handlers
    @Override
    public Receive<String> createReceive() {
        return newReceiveBuilder()
                .onMessage(String.class, this::onMessage)
                .build();
    }

    private Behavior<String> onMessage(String msg) {
        System.out.println("received message: " + msg);
        return this;
    }
}
