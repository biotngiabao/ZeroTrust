<?php
header('Content-Type: application/json; charset=utf-8');
$action = $_GET['action'] ?? '';
if ($action === 'txs' && $_SERVER['REQUEST_METHOD'] === 'GET') {
  $txs = json_decode(file_get_contents(__DIR__ . '/data/txs.json'), true) ?? [];
  echo json_encode($txs);
  exit;
}
if ($action === 'transfer_demo' && $_SERVER['REQUEST_METHOD'] === 'POST') {
  $input = json_decode(file_get_contents('php://input'), true) ?? [];
  $from = $input['from'] ?? 'alice';
  $to = $input['to'] ?? 'bob';
  $amount = floatval($input['amount'] ?? 0);
  $txs = json_decode(file_get_contents(__DIR__ . '/data/txs.json'), true) ?? [];
  $txs[] = ['id'=>time(),'from'=>$from,'to'=>$to,'amount'=>$amount,'date'=>date('c')];
  file_put_contents(__DIR__ . '/data/txs.json', json_encode($txs, JSON_PRETTY_PRINT));
  echo json_encode(['ok'=>true,'note'=>'demo transfer recorded']);
  exit;
}
echo json_encode(['ok'=>false,'error'=>'unknown_action']);
