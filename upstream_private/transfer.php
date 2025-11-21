<?php 
include 'templates/header.php'; 
?>
<h2>Transfer (Demo)</h2>
<p style="color:#5b6b7a">This form now calls the smart 'transfer' service.</p>
<div class="card">
<form method="post" action="transfer.php" style="display:grid;gap:12px;max-width:520px">
  <label>From (username): <input name="from_username" value="alice" required></label>
  <label>To (username): <input name="to_username" value="bob" required></label>
  <label>Amount: <input name="amount" value="100.00" required></label>
  <div style="display:flex;gap:8px">
    <button class="btn btn-primary" type="submit">Send (demo)</button>
    <button class="btn btn-ghost1" type="button" onclick="location.href='transactions.php'">View Transactions</button>
  </div>
</form>
</div>
<?php

$message = '';
$message_type = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  include_once 'lib.php';

  $from = $_POST['from_username'] ?? '';
  $to = $_POST['to_username'] ?? '';
  $amount = floatval($_POST['amount'] ?? 0);

  $transfer_request = [
    'from' => $from,
    'to' => $to,
    'amount' => $amount
  ];

  $response_json = callDataService('POST', 'transfer', $transfer_request);
  $response_data = json_decode($response_json, true);

  if ($response_data && $response_data['ok']) {
      $tx_id = $response_data['transaction']['id'] ?? 'N/A';
      $message = 'Chuyển khoản thành công! (Service đã xử lý và cập nhật số dư). Transaction ID: ' . $tx_id;
      $message_type = 'note';
  } else {
      $error_details = $response_data['error'] ?? 'Unknown service error';
      $message = 'Giao dịch thất bại: ' . htmlspecialchars($error_details);
      $message_type = 'error';
  }
}

if ($message) {
  if ($message_type === 'error') {
    echo '<p class="note" style="color:red;border-color:red;margin-top:15px;">' . $message . '</p>';
  } else {
    echo '<p class="note" style="color:green;border-color:green;margin-top:15px;">' . $message . '</p>';
  }
}
?>
<?php include 'templates/footer.php'; ?>