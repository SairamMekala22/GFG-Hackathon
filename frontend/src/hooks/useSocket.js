import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5050";

export function useSocket(sessionId, onDashboardEvent) {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      return undefined;
    }

    const nextSocket = io(SOCKET_URL, {
      transports: ["websocket"],
      query: { session_id: sessionId }
    });

    nextSocket.on("connect", () => setIsConnected(true));
    nextSocket.on("disconnect", () => setIsConnected(false));
    nextSocket.on("dashboard_updated", onDashboardEvent);

    setSocket(nextSocket);

    return () => {
      nextSocket.disconnect();
    };
  }, [sessionId, onDashboardEvent]);

  return { socket, isConnected };
}
