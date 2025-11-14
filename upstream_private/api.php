<?php
include_once 'lib.php';
header('Content-Type: application/json; charset=utf-8');

$action = $_GET['action'] ?? '';

if ($action === 'txs' && $_SERVER['REQUEST_METHOD'] === 'GET') {
  echo callDataService('GET', 'txs');
  exit;
}

if ($action === 'transfer_demo' && $_SERVER['REQUEST_METHOD'] === 'POST') {
  $input = json_decode(file_get_contents('php://input'), true) ?? [];
  $from = $input['from'] ?? 'alice';
  $to = $input['to'] ?? 'bob';
  $amount = floatval($input['amount'] ?? 0);
  
  $transfer_request = [
    'from' => $from,
    'to' => $to,
    'amount' => $amount
  ];

  $response = callDataService('POST', 'transfer', $transfer_request);
  
  $response_data = json_decode($response, true);
  if ($response_data && $response_data['ok']) {
      echo json_encode(['ok'=>true,'note'=>'demo transfer processed by service', 'transaction' => $response_data['transaction']]);
  } else {
      http_response_code(400);
      echo $response;
  }
  exit;
}

echo json_encode(['ok'=>false,'error'=>'unknown_action']);
?>