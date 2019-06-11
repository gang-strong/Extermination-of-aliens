import pygame
from pygame.sprite import Group

from ship import Ship
from alien import Alien
from setting import Settings
from game_stats import GameStat
from button import Button
from scoreboard import Scoreboard
import game_functions as gf

def run_game():
	#初始化游戏并创建一个屏幕对象
	pygame.init()
	ai_settings = Settings()
	screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
	pygame.display.set_caption("人机大战")
	
	#play按钮
	play_button = Button(ai_settings, screen, "play")
	
	
	#创建一个用于存储游戏统计信息的实例
	stats = GameStat(ai_settings)
	sb = Scoreboard(ai_settings, screen, stats)
	
	ship = Ship(ai_settings, screen)
	#alien = Alien(ai_settings, screen)
	
	# 创建一个用于存储子弹的编组
	bullets = Group() 
	aliens = Group()
	
	gf.create_fleet(ai_settings, screen, ship, aliens)
	
	#游戏主循环
	while True:
		gf.check_events(ai_settings, screen, stats, play_button, ship, sb,
			aliens, bullets)
		if stats.game_active:
			ship.update()
			gf.update_bullets(ai_settings, screen, ship, stats, sb, aliens, bullets)
			gf.update_aliens(ai_settings, stats, screen, ship, sb, aliens, bullets)
		gf.update_screen(ai_settings, screen, ship, sb, aliens, bullets, stats, play_button)
		
run_game()
