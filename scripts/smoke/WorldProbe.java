import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;

/** Local test entry point. The release archive never includes this mod. */
public class WorldProbe implements ClientModInitializer {
    private boolean started;
    private int seconds;
    private long nextSample;

    @Override
    public void onInitializeClient() {
        Thread.startVirtualThread(() -> {
            try {
                while (true) {
                    Thread.sleep(1000);
                    Minecraft game = Minecraft.getInstance();
                    if (game != null) {
                        game.execute(() -> checkWorld(game));
                    }
                }
            } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
            }
        });
    }

    private void checkWorld(Minecraft game) {
        if (!started && game.gui.screen() instanceof TitleScreen title) {
            started = true;
            game.createWorldOpenFlows().createFreshLevel("AfterHoursQA", MinecraftServer.DEMO_SETTINGS,
                WorldOptions.DEMO_OPTIONS, WorldPresets::createNormalWorldDimensions, title);
            return;
        }
        if (game.level == null || game.player == null || game.gui.screen() != null) {
            return;
        }
        long now = System.nanoTime();
        if (now < nextSample) {
            return;
        }
        nextSample = now + 800_000_000L;
        seconds++;
        if (seconds == 45) {
            var server = game.getSingleplayerServer();
            server.execute(() -> server.getCommands().performPrefixedCommand(
                server.createCommandSourceStack(), "weather rain"));
        }
        if ((seconds >= 25 && seconds < 45) || seconds >= 65) {
            System.out.printf("AFTERHOURS_SAMPLE %s %d %dx%d %d %d%n",
                seconds < 45 ? "clear" : "rain", game.getFps(),
                game.getWindow().getWidth(), game.getWindow().getHeight(),
                game.options.renderDistance().get(), game.options.simulationDistance().get());
        }
        if (seconds == 84) {
            System.out.println("AFTERHOURS_WORLD_OK");
            game.stop();
        }
    }
}
