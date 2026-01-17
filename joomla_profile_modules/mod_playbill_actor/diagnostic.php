<?php
defined('_JEXEC') or die;

echo "=== PLAYBILL ACTOR MODULE DIAGNOSTIC ===\n\n";

echo "1. Testing API Connection...\n";
$api_url = 'https://www.broadwayandmain.com/playbill_app/api/joomla/actor/78';
echo "   URL: $api_url\n";

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

echo "   HTTP Code: $http_code\n";
if ($curl_error) {
    echo "   CURL Error: $curl_error\n";
} else {
    echo "   Response Length: " . strlen($response) . " bytes\n";
    if ($http_code === 200) {
        $data = json_decode($response, true);
        if ($data) {
            echo "   ✓ API returned valid JSON\n";
            echo "   Actor ID: " . (isset($data['id']) ? $data['id'] : 'NOT FOUND') . "\n";
            echo "   Actor Name: " . (isset($data['name']) ? $data['name'] : 'NOT FOUND') . "\n";
            echo "   Credits Count: " . (isset($data['credits']) && is_array($data['credits']) ? count($data['credits']) : 0) . "\n";
        } else {
            echo "   ✗ API returned invalid JSON\n";
            echo "   Response preview: " . substr($response, 0, 200) . "\n";
        }
    } else {
        echo "   ✗ API returned error code: $http_code\n";
        echo "   Response: " . substr($response, 0, 200) . "\n";
    }
}

echo "\n2. Testing Module File...\n";
$module_file = __DIR__ . '/mod_playbill_actor.php';
if (file_exists($module_file)) {
    echo "   ✓ Module file exists: $module_file\n";
} else {
    echo "   ✗ Module file NOT found: $module_file\n";
}

echo "\n3. Testing Helper File...\n";
$helper_file = __DIR__ . '/helper/mod_playbill_actor.php';
if (file_exists($helper_file)) {
    echo "   ✓ Helper file exists: $helper_file\n";
} else {
    echo "   ✗ Helper file NOT found: $helper_file\n";
}

echo "\n4. Testing Template File...\n";
$template_file = __DIR__ . '/tmpl/default.php';
if (file_exists($template_file)) {
    echo "   ✓ Template file exists: $template_file\n";
} else {
    echo "   ✗ Template file NOT found: $template_file\n";
}

echo "\n=== END DIAGNOSTIC ===\n";

