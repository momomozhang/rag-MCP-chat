# transports

Source: https://modelcontextprotocol.io/docs/concepts/transports/

[Model Context Protocol home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/dark.svg)](/)

Search...

* [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
* [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
* [Java SDK](https://github.com/modelcontextprotocol/java-sdk)
* [Kotlin SDK](https://github.com/modelcontextprotocol/kotlin-sdk)
* [C# SDK](https://github.com/modelcontextprotocol/csharp-sdk)
* [Swift SDK](https://github.com/modelcontextprotocol/swift-sdk)

##### Get Started

  * [Introduction](/introduction)
  * Quickstart

  * [Example Servers](/examples)
  * [Example Clients](/clients)
  * [FAQs](/faqs)

##### Tutorials

  * [Building MCP with LLMs](/tutorials/building-mcp-with-llms)
  * [Debugging](/docs/tools/debugging)
  * [Inspector](/docs/tools/inspector)

##### Concepts

  * [Core architecture](/docs/concepts/architecture)
  * [Resources](/docs/concepts/resources)
  * [Prompts](/docs/concepts/prompts)
  * [Tools](/docs/concepts/tools)
  * [Sampling](/docs/concepts/sampling)
  * [Roots](/docs/concepts/roots)
  * [Transports](/docs/concepts/transports)

##### Development

  * [What's New](/development/updates)
  * [Roadmap](/development/roadmap)
  * [Contributing](/development/contributing)

[Model Context Protocol home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/dark.svg)](/)

Search...

  * [GitHub](https://github.com/modelcontextprotocol)
  * [GitHub](https://github.com/modelcontextprotocol)

Search...

Navigation

Concepts

Transports

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

* [GitHub](https://github.com/modelcontextprotocol)

Concepts

# Transports

Copy page

Learn about MCP’s communication mechanisms

Transports in the Model Context Protocol (MCP) provide the foundation for
communication between clients and servers. A transport handles the underlying
mechanics of how messages are sent and received.

##

​

Message Format

MCP uses [JSON-RPC](https://www.jsonrpc.org/) 2.0 as its wire format. The
transport layer is responsible for converting MCP protocol messages into JSON-
RPC format for transmission and converting received JSON-RPC messages back
into MCP protocol messages.

There are three types of JSON-RPC messages used:

###

​

Requests

    
    
    {
      jsonrpc: "2.0",
      id: number | string,
      method: string,
      params?: object
    }
    

###

​

Responses

    
    
    {
      jsonrpc: "2.0",
      id: number | string,
      result?: object,
      error?: {
        code: number,
        message: string,
        data?: unknown
      }
    }
    

###

​

Notifications

    
    
    {
      jsonrpc: "2.0",
      method: string,
      params?: object
    }
    

##

​

Built-in Transport Types

MCP includes two standard transport implementations:

###

​

Standard Input/Output (stdio)

The stdio transport enables communication through standard input and output
streams. This is particularly useful for local integrations and command-line
tools.

Use stdio when:

  * Building command-line tools
  * Implementing local integrations
  * Needing simple process communication
  * Working with shell scripts

  * TypeScript (Server)
  * TypeScript (Client)
  * Python (Server)
  * Python (Client)

    
    
    const server = new Server({
      name: "example-server",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    
    
    const server = new Server({
      name: "example-server",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    
    
    const client = new Client({
      name: "example-client",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    const transport = new StdioClientTransport({
      command: "./server",
      args: ["--option", "value"]
    });
    await client.connect(transport);
    
    
    
    app = Server("example-server")
    
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )
    
    
    
    params = StdioServerParameters(
        command="./server",
        args=["--option", "value"]
    )
    
    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
    

###

​

Server-Sent Events (SSE)

SSE transport enables server-to-client streaming with HTTP POST requests for
client-to-server communication.

Use SSE when:

  * Only server-to-client streaming is needed
  * Working with restricted networks
  * Implementing simple updates

####

​

Security Warning: DNS Rebinding Attacks

SSE transports can be vulnerable to DNS rebinding attacks if not properly
secured. To prevent this:

  1. **Always validate Origin headers** on incoming SSE connections to ensure they come from expected sources
  2. **Avoid binding servers to all network interfaces** (0.0.0.0) when running locally - bind only to localhost (127.0.0.1) instead
  3. **Implement proper authentication** for all SSE connections

Without these protections, attackers could use DNS rebinding to interact with
local MCP servers from remote websites.

  * TypeScript (Server)
  * TypeScript (Client)
  * Python (Server)
  * Python (Client)

    
    
    import express from "express";
    
    const app = express();
    
    const server = new Server({
      name: "example-server",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    let transport: SSEServerTransport | null = null;
    
    app.get("/sse", (req, res) => {
      transport = new SSEServerTransport("/messages", res);
      server.connect(transport);
    });
    
    app.post("/messages", (req, res) => {
      if (transport) {
        transport.handlePostMessage(req, res);
      }
    });
    
    app.listen(3000);
    
    
    
    import express from "express";
    
    const app = express();
    
    const server = new Server({
      name: "example-server",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    let transport: SSEServerTransport | null = null;
    
    app.get("/sse", (req, res) => {
      transport = new SSEServerTransport("/messages", res);
      server.connect(transport);
    });
    
    app.post("/messages", (req, res) => {
      if (transport) {
        transport.handlePostMessage(req, res);
      }
    });
    
    app.listen(3000);
    
    
    
    const client = new Client({
      name: "example-client",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    
    const transport = new SSEClientTransport(
      new URL("http://localhost:3000/sse")
    );
    await client.connect(transport);
    
    
    
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    
    app = Server("example-server")
    sse = SseServerTransport("/messages")
    
    async def handle_sse(scope, receive, send):
        async with sse.connect_sse(scope, receive, send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
    
    async def handle_messages(scope, receive, send):
        await sse.handle_post_message(scope, receive, send)
    
    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )
    
    
    
    async with sse_client("http://localhost:8000/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
    

##

​

Custom Transports

MCP makes it easy to implement custom transports for specific needs. Any
transport implementation just needs to conform to the Transport interface:

You can implement custom transports for:

  * Custom network protocols
  * Specialized communication channels
  * Integration with existing systems
  * Performance optimization

  * TypeScript
  * Python

    
    
    interface Transport {
      // Start processing messages
      start(): Promise<void>;
    
      // Send a JSON-RPC message
      send(message: JSONRPCMessage): Promise<void>;
    
      // Close the connection
      close(): Promise<void>;
    
      // Callbacks
      onclose?: () => void;
      onerror?: (error: Error) => void;
      onmessage?: (message: JSONRPCMessage) => void;
    }
    
    
    
    interface Transport {
      // Start processing messages
      start(): Promise<void>;
    
      // Send a JSON-RPC message
      send(message: JSONRPCMessage): Promise<void>;
    
      // Close the connection
      close(): Promise<void>;
    
      // Callbacks
      onclose?: () => void;
      onerror?: (error: Error) => void;
      onmessage?: (message: JSONRPCMessage) => void;
    }
    

Note that while MCP Servers are often implemented with asyncio, we recommend
implementing low-level interfaces like transports with `anyio` for wider
compatibility.

    
    
    @contextmanager
    async def create_transport(
        read_stream: MemoryObjectReceiveStream[JSONRPCMessage | Exception],
        write_stream: MemoryObjectSendStream[JSONRPCMessage]
    ):
        """
        Transport interface for MCP.
    
        Args:
            read_stream: Stream to read incoming messages from
            write_stream: Stream to write outgoing messages to
        """
        async with anyio.create_task_group() as tg:
            try:
                # Start processing messages
                tg.start_soon(lambda: process_messages(read_stream))
    
                # Send messages
                async with write_stream:
                    yield write_stream
    
            except Exception as exc:
                # Handle errors
                raise exc
            finally:
                # Clean up
                tg.cancel_scope.cancel()
                await write_stream.aclose()
                await read_stream.aclose()
    

##

​

Error Handling

Transport implementations should handle various error scenarios:

  1. Connection errors
  2. Message parsing errors
  3. Protocol errors
  4. Network timeouts
  5. Resource cleanup

Example error handling:

  * TypeScript
  * Python

    
    
    class ExampleTransport implements Transport {
      async start() {
        try {
          // Connection logic
        } catch (error) {
          this.onerror?.(new Error(`Failed to connect: ${error}`));
          throw error;
        }
      }
    
      async send(message: JSONRPCMessage) {
        try {
          // Sending logic
        } catch (error) {
          this.onerror?.(new Error(`Failed to send message: ${error}`));
          throw error;
        }
      }
    }
    
    
    
    class ExampleTransport implements Transport {
      async start() {
        try {
          // Connection logic
        } catch (error) {
          this.onerror?.(new Error(`Failed to connect: ${error}`));
          throw error;
        }
      }
    
      async send(message: JSONRPCMessage) {
        try {
          // Sending logic
        } catch (error) {
          this.onerror?.(new Error(`Failed to send message: ${error}`));
          throw error;
        }
      }
    }
    

Note that while MCP Servers are often implemented with asyncio, we recommend
implementing low-level interfaces like transports with `anyio` for wider
compatibility.

    
    
    @contextmanager
    async def example_transport(scope: Scope, receive: Receive, send: Send):
        try:
            # Create streams for bidirectional communication
            read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
            write_stream, write_stream_reader = anyio.create_memory_object_stream(0)
    
            async def message_handler():
                try:
                    async with read_stream_writer:
                        # Message handling logic
                        pass
                except Exception as exc:
                    logger.error(f"Failed to handle message: {exc}")
                    raise exc
    
            async with anyio.create_task_group() as tg:
                tg.start_soon(message_handler)
                try:
                    # Yield streams for communication
                    yield read_stream, write_stream
                except Exception as exc:
                    logger.error(f"Transport error: {exc}")
                    raise exc
                finally:
                    tg.cancel_scope.cancel()
                    await write_stream.aclose()
                    await read_stream.aclose()
        except Exception as exc:
            logger.error(f"Failed to initialize transport: {exc}")
            raise exc
    

##

​

Best Practices

When implementing or using MCP transport:

  1. Handle connection lifecycle properly
  2. Implement proper error handling
  3. Clean up resources on connection close
  4. Use appropriate timeouts
  5. Validate messages before sending
  6. Log transport events for debugging
  7. Implement reconnection logic when appropriate
  8. Handle backpressure in message queues
  9. Monitor connection health
  10. Implement proper security measures

##

​

Security Considerations

When implementing transport:

###

​

Authentication and Authorization

  * Implement proper authentication mechanisms
  * Validate client credentials
  * Use secure token handling
  * Implement authorization checks

###

​

Data Security

  * Use TLS for network transport
  * Encrypt sensitive data
  * Validate message integrity
  * Implement message size limits
  * Sanitize input data

###

​

Network Security

  * Implement rate limiting
  * Use appropriate timeouts
  * Handle denial of service scenarios
  * Monitor for unusual patterns
  * Implement proper firewall rules
  * For SSE transports, validate Origin headers to prevent DNS rebinding attacks
  * For local SSE servers, bind only to localhost (127.0.0.1) instead of all interfaces (0.0.0.0)

##

​

Debugging Transport

Tips for debugging transport issues:

  1. Enable debug logging
  2. Monitor message flow
  3. Check connection states
  4. Validate message formats
  5. Test error scenarios
  6. Use network analysis tools
  7. Implement health checks
  8. Monitor resource usage
  9. Test edge cases
  10. Use proper error tracking

Was this page helpful?

YesNo

[Roots](/docs/concepts/roots)[What's New](/development/updates)

[github](https://github.com/modelcontextprotocol)

On this page

  * Message Format
  * Requests
  * Responses
  * Notifications
  * Built-in Transport Types
  * Standard Input/Output (stdio)
  * Server-Sent Events (SSE)
  * Security Warning: DNS Rebinding Attacks
  * Custom Transports
  * Error Handling
  * Best Practices
  * Security Considerations
  * Authentication and Authorization
  * Data Security
  * Network Security
  * Debugging Transport

Assistant

Responses are generated using AI and may contain mistakes.

