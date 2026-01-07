<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\CMS\Log\Log;

class PlgContentPlaybill extends CMSPlugin
{
    protected $app;
    protected $api_base_url;
    protected $public_base_url;
    
    public function __construct(&$subject, $config)
    {
        parent::__construct($subject, $config);
        $this->app = Factory::getApplication();
        $this->api_base_url = $this->params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
        $this->public_base_url = $this->params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
    }
    
    public function onContentPrepare($context, &$article, &$params, $page = 0)
    {
        if (isset($article->text)) {
            $article->text = preg_replace_callback(
                '/\{playbill_show\s+id="(\d+)"(?:\s+production="(\d+)")?\}/',
                [$this, 'renderShow'],
                $article->text
            );
        }
    }
    
    protected function renderShow($matches)
    {
        $show_id = (int)$matches[1];
        $production_id = isset($matches[2]) ? (int)$matches[2] : null;
        
        try {
            $show_data = $this->fetchShowData($show_id);
            if (!$show_data || isset($show_data['error'])) {
                return '<p class="playbill-error">Show not found</p>';
            }
            
            return $this->renderShowHTML($show_data, $production_id);
        } catch (Exception $e) {
            Log::add('Playbill plugin error: ' . $e->getMessage(), Log::ERROR, 'playbill');
            return '<p class="playbill-error">Error loading show data</p>';
        }
    }
    
    protected function fetchShowData($show_id)
    {
        $url = $this->api_base_url . '/show/' . $show_id;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            return null;
        }
        
        return json_decode($response, true);
    }
    
    protected function renderShowHTML($show_data, $production_id = null)
    {
        $html = '<div class="playbill-show" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
        $html .= '<h3 class="playbill-title" style="font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #1f2937;">' . htmlspecialchars($show_data['title']) . '</h3>';
        
        $productions = $production_id 
            ? array_filter($show_data['productions'], function($p) use ($production_id) {
                return $p['id'] == $production_id;
            })
            : $show_data['productions'];
        
        foreach ($productions as $production) {
            $html .= '<div class="playbill-production" style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb;">';
            $html .= '<h4 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #4b5563;">' . htmlspecialchars($production['theater']['name']) . ' (' . $production['year'] . ')</h4>';
            
            $credits_by_category = [];
            foreach ($production['credits'] as $credit) {
                $category = $credit['category'];
                if (!isset($credits_by_category[$category])) {
                    $credits_by_category[$category] = [];
                }
                $credits_by_category[$category][] = $credit;
            }
            
            foreach ($credits_by_category as $category => $credits) {
                $html .= '<div class="playbill-category" style="margin-bottom: 20px;">';
                $html .= '<h5 style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">' . htmlspecialchars($category) . '</h5>';
                $html .= '<ul style="list-style: none; padding: 0; margin: 0;">';
                
                foreach ($credits as $credit) {
                    $person_url = $this->public_base_url . '/actor/' . $credit['person']['id'];
                    $equity_badge = $credit['is_equity'] ? ' <span style="color: #10b981; font-weight: 600;">*</span>' : '';
                    $html .= '<li style="padding: 5px 0; border-bottom: 1px solid #f3f4f6;">';
                    $html .= '<a href="' . $person_url . '" style="color: #4f46e5; text-decoration: none; font-weight: 500;">' . htmlspecialchars($credit['person']['name']) . '</a>';
                    if ($credit['role']) {
                        $html .= ' <span style="color: #6b7280;">as ' . htmlspecialchars($credit['role']) . '</span>';
                    }
                    $html .= $equity_badge;
                    $html .= '</li>';
                }
                
                $html .= '</ul>';
                $html .= '</div>';
            }
            
            $html .= '</div>';
        }
        
        $html .= '</div>';
        return $html;
    }
}

