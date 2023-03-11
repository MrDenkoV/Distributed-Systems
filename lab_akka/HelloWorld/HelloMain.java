package HelloWorld;

import akka.actor.typed.ActorSystem;

public class HelloMain {

    public static void main(String[] args) throws Exception {

        // create actor system
        final ActorSystem<String> system =
                ActorSystem.create(HelloActor.create(), "helloActor");

        // send messages
        system.tell("hello world");

    }
}
