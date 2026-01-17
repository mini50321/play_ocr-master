<?php
defined('_JEXEC') or die;

use Joomla\CMS\Log\Log;
use Joomla\CMS\Factory;

class ModPlaybillActorHelper
{
    public static function getActorData($actor_id, $api_base_url, $public_base_url)
    {
        if (empty($actor_id)) {
            return null;
        }
        
        $url = $api_base_url . '/actor/' . urlencode($actor_id);
        Log::add('Playbill actor module: Fetching data from ' . $url . ' for actor ID ' . $actor_id, Log::INFO, 'mod_playbill_actor');
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error = curl_error($ch);
        curl_close($ch);
        
        if ($curl_error) {
            Log::add('Playbill actor module CURL error for actor ID ' . $actor_id . ': ' . $curl_error, Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        if ($http_code !== 200) {
            Log::add('Playbill actor module error: HTTP ' . $http_code . ' for actor ID ' . $actor_id . '. Response: ' . substr($response, 0, 200), Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        if (empty($response)) {
            Log::add('Playbill actor module: Empty response for actor ID ' . $actor_id, Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        $data = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            Log::add('Playbill actor module JSON error: ' . json_last_error_msg() . ' for actor ID ' . $actor_id . '. Response preview: ' . substr($response, 0, 200), Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        if (!$data || isset($data['error'])) {
            $error_msg = isset($data['error']) ? $data['error'] : 'Invalid data structure';
            Log::add('Playbill actor module: Invalid data or error in response for actor ID ' . $actor_id . ': ' . $error_msg, Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        if (!isset($data['id']) || (int)$data['id'] !== (int)$actor_id) {
            Log::add('Playbill actor module: Actor ID mismatch. Requested: ' . $actor_id . ', Received: ' . (isset($data['id']) ? $data['id'] : 'none'), Log::WARNING, 'mod_playbill_actor');
        }
        
        if (!isset($data['credits']) || !is_array($data['credits'])) {
            Log::add('Playbill actor module: Missing or invalid credits array for actor ID ' . $actor_id, Log::WARNING, 'mod_playbill_actor');
            $data['credits'] = [];
        } else {
            $valid_credits = [];
            foreach ($data['credits'] as $index => $credit) {
                if (!is_array($credit)) {
                    Log::add('Playbill actor module: Invalid credit at index ' . $index . ' for actor ID ' . $actor_id . ' (not an array)', Log::WARNING, 'mod_playbill_actor');
                    continue;
                }
                $valid_credits[] = $credit;
            }
            $data['credits'] = $valid_credits;
        }
        
        $data['public_base_url'] = $public_base_url;
        return $data;
    }
    
    public static function groupCreditsByCategory($credits)
    {
        $grouped = [];
        if (!is_array($credits)) {
            return $grouped;
        }
        foreach ($credits as $credit) {
            if (!is_array($credit)) {
                continue;
            }
            $category = 'Other';
            if (isset($credit['category']) && !empty($credit['category']) && is_string($credit['category'])) {
                $category = $credit['category'];
            }
            if (!isset($grouped[$category])) {
                $grouped[$category] = [];
            }
            $grouped[$category][] = $credit;
        }
        return $grouped;
    }
}

