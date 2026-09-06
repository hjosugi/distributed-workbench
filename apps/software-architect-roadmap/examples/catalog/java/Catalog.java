import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class Catalog {
    public static void main(String[] args) throws Exception {
        String host = System.getenv().getOrDefault("BIND_HOST", "127.0.0.1");
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "8081"));
        HttpServer server = HttpServer.create(new InetSocketAddress(host, port), 0);
        server.createContext("/", exchange -> {
            String path = exchange.getRequestURI().getPath();
            String body;
            int status;
            if (!exchange.getRequestMethod().equals("GET")) {
                body = "{\"error\":\"method not allowed\"}"; status = 405;
            } else if (path.equals("/products")) {
                body = "[{\"sku\":\"book\",\"unit_price\":1200},{\"sku\":\"pen\",\"unit_price\":200}]"; status = 200;
            } else if (path.equals("/health")) {
                body = "{\"status\":\"ok\"}"; status = 200;
            } else { body = "{\"error\":\"not found\"}"; status = 404; }
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(status, bytes.length);
            try (var stream = exchange.getResponseBody()) { stream.write(bytes); }
        });
        server.start();
        System.out.println("Catalog listening on " + host + ":" + server.getAddress().getPort());
    }
}
