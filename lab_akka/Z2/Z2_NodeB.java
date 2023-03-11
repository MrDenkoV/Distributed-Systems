package Z2;

import akka.actor.typed.*;
import akka.actor.typed.javadsl.Behaviors;
import akka.cluster.typed.*;
import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import java.io.File;


public class Z2_NodeB {

    public static Behavior<Void> create() {
        return Behaviors.setup(
                context -> {

                    // TODO : text service

                    return Behaviors.receive(Void.class)
                            .onSignal(Terminated.class, sig -> Behaviors.stopped())
                            .build();
                });
    }

    public static void main(String[] args) {
        File configFile = new File("src/main/nodeB.conf");
        Config config = ConfigFactory.parseFile(configFile);
        System.out.println("Node B: config: " + config);

        ActorSystem.create(Z2_NodeB.create(), "ClusterSystem", config);
    }
}
