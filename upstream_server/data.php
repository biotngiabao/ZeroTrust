<?php
header('Content-Type: application/json; charset=utf-8');

function send_error($message, $code = 400) {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $message]);
    exit;
}

/**
 * @return array [file_handle, file_data_as_array]
 */
function open_and_lock($filepath) {
    $handle = fopen($filepath, 'c+');
    if (!$handle) {
        send_error('Cannot open data file: ' . basename($filepath), 500);
    }
    if (!flock($handle, LOCK_EX)) {
        fclose($handle);
        send_error('Cannot lock data file: ' . basename($filepath), 500);
    }
    
    $raw_content = stream_get_contents($handle);
    $data = json_decode($raw_content, true);
    
    if ($data === null) {
        $data = str_ends_with($filepath, 'accounts.json') ? (object)[] : [];
    }
    
    return [$handle, $data];
}

function write_unlock_close($handle, $data) {
    ftruncate($handle, 0);
    fseek($handle, 0);
    fwrite($handle, json_encode($data, JSON_PRETTY_PRINT));
    flock($handle, LOCK_UN);
    fclose($handle);
}

$headers = getallheaders();
$token = $headers['Token'] ?? $headers['token'] ?? null;
$key = $headers['Key'] ?? $headers['key'] ?? null;

// if (!$token || !$key) {
//     send_error('Missing required headers (Token or Key)', 401);
// }

$method = $_SERVER['REQUEST_METHOD'];
$resource = $_GET['resource'] ?? '';
$data_dir = __DIR__ . '/data/';


if ($method === 'GET') {
    $file_path = '';
    switch ($resource) {
        case 'txs':
            $file_path = $data_dir . 'txs.json';
            break;
        case 'accounts':
            $file_path = $data_dir . 'accounts.json';
            break;
        case 'contact_log':
            $file_path = $data_dir . 'contact_log.json';
            break;
        default:
            send_error('Unknown resource', 404);
    }
    
    if (!file_exists($file_path)) {
        echo '[]';
        exit;
    }
    
    $content = file_get_contents($file_path);
    echo $content;
    exit;
}

if ($method === 'POST') {
    $input_data = json_decode(file_get_contents('php://input'), true);
    if ($input_data === null) {
        send_error('Invalid JSON payload');
    }
    
    switch ($resource) {
        case 'transfer':
            $from = $input_data['from'] ?? null;
            $to = $input_data['to'] ?? null;
            $amount = floatval($input_data['amount'] ?? 0);
            
            if (!$from || !$to || $amount <= 0) {
                send_error('Invalid transfer request: "from", "to", and "amount" > 0 are required.');
            }
            
            $accounts_file = $data_dir . 'accounts.json';
            $txs_file = $data_dir . 'txs.json';
            
            list($accounts_handle, $accounts_data) = open_and_lock($accounts_file);
            list($txs_handle, $txs_data) = open_and_lock($txs_file);
            
            if (!isset($accounts_data[$from])) {
                send_error('Sender account not found', 404);
            }
            if (!isset($accounts_data[$to])) {
                send_error('Receiver account not found', 404);
            }
            
            $from_balance = floatval($accounts_data[$from]['balance']);
            
            if ($from_balance < $amount) {
                flock($accounts_handle, LOCK_UN);
                fclose($accounts_handle);
                flock($txs_handle, LOCK_UN);
                fclose($txs_handle);
                
                send_error('Tài khoản không đủ số dư', 402);
            }
            
            $accounts_data[$from]['balance'] -= $amount;
            $accounts_data[$to]['balance'] += $amount;
            
            $new_tx = [
                'id' => time(),
                'from' => $from,
                'to' => $to,
                'amount' => $amount,
                'date' => date('c')
            ];
            $txs_data[] = $new_tx;
            
            write_unlock_close($accounts_handle, $accounts_data);
            write_unlock_close($txs_handle, $txs_data);
            
            echo json_encode(['ok' => true, 'transaction' => $new_tx]);
            exit;
            
        default:
            send_error('Unknown POST resource', 404);
    }
}

send_error('Method not allowed', 405);
?>