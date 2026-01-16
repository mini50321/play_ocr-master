<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\CMS\Log\Log;

class PlgContentPlaybillProfile extends CMSPlugin
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
                '/\{playbill_actor\s+id="(\d+)"\}/',
                [$this, 'renderActor'],
                $article->text
            );
            
            $article->text = preg_replace_callback(
                '/\{playbill_show\s+id="(\d+)"\}/',
                [$this, 'renderShow'],
                $article->text
            );
            
            $article->text = preg_replace_callback(
                '/\{playbill_theater\s+id="(\d+)"\}/',
                [$this, 'renderTheater'],
                $article->text
            );
        }
    }
    
    protected function renderActor($matches)
    {
        $actor_id = (int)$matches[1];
        
        try {
            $actor_data = $this->fetchActorData($actor_id);
            if (!$actor_data || isset($actor_data['error'])) {
                return '<p class="playbill-error">Actor not found</p>';
            }
            
            return $this->renderActorHTML($actor_data);
        } catch (Exception $e) {
            Log::add('Playbill profile plugin error: ' . $e->getMessage(), Log::ERROR, 'playbill_profile');
            return '<p class="playbill-error">Error loading actor data</p>';
        }
    }
    
    protected function renderShow($matches)
    {
        $show_id = (int)$matches[1];
        
        try {
            $show_data = $this->fetchShowData($show_id);
            if (!$show_data || isset($show_data['error'])) {
                return '<p class="playbill-error">Show not found</p>';
            }
            
            return $this->renderShowHTML($show_data);
        } catch (Exception $e) {
            Log::add('Playbill profile plugin error: ' . $e->getMessage(), Log::ERROR, 'playbill_profile');
            return '<p class="playbill-error">Error loading show data</p>';
        }
    }
    
    protected function renderTheater($matches)
    {
        $theater_id = (int)$matches[1];
        
        try {
            $theater_data = $this->fetchTheaterData($theater_id);
            if (!$theater_data || isset($theater_data['error'])) {
                return '<p class="playbill-error">Theater not found</p>';
            }
            
            return $this->renderTheaterHTML($theater_data);
        } catch (Exception $e) {
            Log::add('Playbill profile plugin error: ' . $e->getMessage(), Log::ERROR, 'playbill_profile');
            return '<p class="playbill-error">Error loading theater data</p>';
        }
    }
    
    protected function fetchActorData($actor_id)
    {
        $url = $this->api_base_url . '/actor/' . $actor_id;
        return $this->fetchJSON($url);
    }
    
    protected function fetchShowData($show_id)
    {
        $url = $this->api_base_url . '/show/' . $show_id;
        return $this->fetchJSON($url);
    }
    
    protected function fetchTheaterData($theater_id)
    {
        $url = $this->api_base_url . '/theater/' . $theater_id;
        return $this->fetchJSON($url);
    }
    
    protected function fetchJSON($url)
    {
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
    
    protected function renderActorHTML($actor_data)
    {
        $html = '<div class="playbill-actor-profile" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
        $html .= '<h3 style="font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
        $html .= '<a href="' . htmlspecialchars($this->public_base_url . '/actor/' . $actor_data['id']) . '" style="color: #4f46e5; text-decoration: none;">';
        $html .= htmlspecialchars($actor_data['name']);
        $html .= '</a></h3>';
        
        if (!empty($actor_data['credits'])) {
            $html .= '<p style="color: #6b7280; margin-bottom: 15px;">' . count($actor_data['credits']) . ' credit(s)</p>';
            
            $credits_by_category = [];
            foreach ($actor_data['credits'] as $credit) {
                $category = $credit['category'];
                if (!isset($credits_by_category[$category])) {
                    $credits_by_category[$category] = [];
                }
                $credits_by_category[$category][] = $credit;
            }
            
            foreach ($credits_by_category as $category => $credits) {
                $html .= '<div style="margin-bottom: 20px;">';
                $html .= '<h4 style="font-size: 18px; font-weight: 600; margin-bottom: 10px; color: #4b5563;">' . htmlspecialchars($category) . '</h4>';
                $html .= '<ul style="list-style: none; padding: 0; margin: 0;">';
                
                foreach (array_slice($credits, 0, 5) as $credit) {
                    $html .= '<li style="padding: 5px 0;">';
                    $html .= '<strong>' . htmlspecialchars($credit['show']['title']) . '</strong>';
                    if ($credit['role'] && $credit['role'] !== $category) {
                        $html .= ' - ' . htmlspecialchars($credit['role']);
                    }
                    $html .= ' (' . (int)$credit['year'] . ')';
                    if ($credit['is_equity']) {
                        $html .= ' <span style="color: #10b981; font-weight: 600;">*</span>';
                    }
                    $html .= '</li>';
                }
                
                if (count($credits) > 5) {
                    $html .= '<li style="padding: 5px 0; color: #6b7280;">... and ' . (count($credits) - 5) . ' more</li>';
                }
                
                $html .= '</ul></div>';
            }
        }
        
        $html .= '<p style="margin-top: 15px;"><a href="' . htmlspecialchars($this->public_base_url . '/actor/' . $actor_data['id']) . '" style="color: #4f46e5; text-decoration: none; font-weight: 500;">View full profile →</a></p>';
        $html .= '</div>';
        
        return $html;
    }
    
    protected function renderShowHTML($show_data)
    {
        $html = '<div class="playbill-show-profile" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
        $html .= '<h3 style="font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
        $html .= '<a href="' . htmlspecialchars($this->public_base_url . '/show/' . $show_data['id']) . '" style="color: #4f46e5; text-decoration: none;">';
        $html .= htmlspecialchars($show_data['title']);
        $html .= '</a></h3>';
        
        if (!empty($show_data['productions'])) {
            $html .= '<p style="color: #6b7280; margin-bottom: 15px;">' . count($show_data['productions']) . ' production(s)</p>';
            
            foreach (array_slice($show_data['productions'], 0, 3) as $production) {
                $html .= '<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #f3f4f6;">';
                $html .= '<strong>' . htmlspecialchars($production['theater']['name']) . '</strong> (' . (int)$production['year'] . ')';
                $html .= '</div>';
            }
            
            if (count($show_data['productions']) > 3) {
                $html .= '<p style="color: #6b7280;">... and ' . (count($show_data['productions']) - 3) . ' more production(s)</p>';
            }
        }
        
        $html .= '<p style="margin-top: 15px;"><a href="' . htmlspecialchars($this->public_base_url . '/show/' . $show_data['id']) . '" style="color: #4f46e5; text-decoration: none; font-weight: 500;">View full profile →</a></p>';
        $html .= '</div>';
        
        return $html;
    }
    
    protected function renderTheaterHTML($theater_data)
    {
        $html = '<div class="playbill-theater-profile" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
        $html .= '<h3 style="font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
        $html .= '<a href="' . htmlspecialchars($this->public_base_url . '/theater/' . $theater_data['id']) . '" style="color: #4f46e5; text-decoration: none;">';
        $html .= htmlspecialchars($theater_data['name']);
        $html .= '</a></h3>';
        
        if (!empty($theater_data['address'])) {
            $html .= '<p style="color: #6b7280; margin-bottom: 10px;">' . htmlspecialchars($theater_data['address']) . '</p>';
        }
        
        if (!empty($theater_data['shows'])) {
            $total_productions = 0;
            foreach ($theater_data['shows'] as $show_group) {
                $total_productions += count($show_group['productions']);
            }
            
            $html .= '<p style="color: #6b7280; margin-bottom: 15px;">' . count($theater_data['shows']) . ' show(s), ' . $total_productions . ' production(s)</p>';
        }
        
        $html .= '<p style="margin-top: 15px;"><a href="' . htmlspecialchars($this->public_base_url . '/theater/' . $theater_data['id']) . '" style="color: #4f46e5; text-decoration: none; font-weight: 500;">View full profile →</a></p>';
        $html .= '</div>';
        
        return $html;
    }
}

