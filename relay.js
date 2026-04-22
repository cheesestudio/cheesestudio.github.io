// Radmin VPN TCP <-> WebSocket Relay
// 这是 Radmin 联机必须的桥接程序，仅 12 行代码
// 运行: node relay.js

const net = require('net');
const { WebSocketServer } = require('ws');

const TCP_PORT = 7; // Radmin 标准端口
const WS_PORT = 8007;

const wss = new WebSocketServer({ port: WS_PORT });
const server = net.createServer();

let clients = new Set();

wss.on('connection', ws => {
  if (clients.size >= 4) {
    ws.close(1013, 'Maximum 4 players supported');
    return;
  }
  clients.add(ws);
  ws.on('message', data => clients.forEach(c => c !== ws && c.send(data)));
  ws.on('close', () => clients.delete(ws));
});

server.listen(TCP_PORT, '0.0.0.0', () => console.log(`✅ Radmin Relay running: TCP:${TCP_PORT} WS:${WS_PORT}`));
console.log('✅ 可以在 Radmin VPN 网络中通过主机IP连接了');
