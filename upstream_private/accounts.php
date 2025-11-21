<?php 
include 'templates/header.php'; 
include_once 'lib.php';
?>
<h2>Accounts (Demo)</h2>

<?php
$json_response = callDataService('GET', 'accounts');
$accounts = json_decode($json_response, true);

if (!$accounts || !is_array($accounts) || (isset($accounts['ok']) && $accounts['ok'] === false)) {
    echo "<p> $accounts</p>";
    echo "<p class='note' style='color:red;border-color:red;'>Could not load account data from service.</p>";
    
    if(isset($accounts['error'])) {
        $error_details = $accounts['details'] ?? $accounts['error'] ?? 'unknown_service_error';
        echo "<p style='color:red'>" . htmlspecialchars($error_details) . "</p>";
    }
} else {
?>
    <table class='table'>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Username</th>
                <th>Balance</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php
            foreach ($accounts as $username => $data) {
                echo "<tr>";
                echo "<td>" . htmlspecialchars($data['id'] ?? 'N/A') . "</td>";
                echo "<td>" . htmlspecialchars($data['name'] ?? 'N/A') . "</td>";
                echo "<td>" . htmlspecialchars($username) . "</td>";
                echo "<td>" . htmlspecialchars($data['balance'] ?? '0') . "</td>";
                
                echo "<td>";
                if ($username === 'admin') {
                    echo "<button class=\"btn btn-danger\" onclick=\"location.href='http://localhost:8000/admin.php'\">Admin</button>";
                } else {
                    echo "<button class=\"btn btn-ghost1\" onclick=\"location.href='transfer.php'\">Transfer</button> ";
                    echo "<button class=\"btn btn-ghost1\" onclick=\"location.href='transactions.php'\">View Tx</button>";
                }
                echo "</td>";
                echo "</tr>";
            }
            ?>
        </tbody>
    </table>
<?php
}
?>

<?php include 'templates/footer.php'; ?>