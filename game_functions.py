import sys
from time import sleep
import pygame

from bullet import Bullet
from alien import Alien 

def check_keydown_event(event, ai_settings, screen, stats, ship, bullets):
	if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:#q键退出
		exit("goodbyte!")
	elif event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullet(ai_settings, screen, stats, ship, bullets)
		
def check_keyup_event(event, ship):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False

def check_events(ai_settings, screen, stats, play_button, ship, sb, aliens,
		bullets):
	#响应按键和鼠标事件
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit("goodbyte!")
		elif event.type == pygame.KEYDOWN:
			check_keydown_event(event, ai_settings, screen, stats, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_event(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, play_button,
				ship, sb, aliens, bullets, mouse_x, mouse_y)

def fire_bullet(ai_settings, screen, stats, ship, bullets):
	"""子弹数限制3个以内"""
	if stats.game_active and len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)

def update_screen(ai_settings, screen, ship, sb, aliens, bullets, stats, play_button):
	#每次循环重绘屏幕
	screen.fill(ai_settings.bg_color)
	# 在飞船和外星人后面重绘所有子弹
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	#alien.blitme()
	aliens.draw(screen)
	
	#显示得分
	sb.show_score()
	
	#如果游戏处于非活动状态，绘制开始游戏
	if not stats.game_active:
		play_button.draw_button()
	
	#最近绘制的屏幕可见
	pygame.display.flip()

def update_bullets(ai_settings, screen, ship, stats, sb, aliens, bullets):
	"""更新子弹位置, 删除消失的子弹"""
	bullets.update()
	
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	check_bullet_alien_collisions(ai_settings, screen, ship, stats, sb, aliens, bullets)
	

def check_bullet_alien_collisions(ai_settings, screen, ship, stats, sb, aliens, bullets):
	"""响应子弹和外星人的碰撞"""
	# 检查是否有子弹击中了外星人
	# 如果是这样， 就删除相应的子弹和外星人 返回结果为字典
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	
	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points * len(aliens)
			sb.prep_score()
		check_high_score(stats, sb)
	
	#检查外星人是否存在  不存在重新创建
	if len(aliens) == 0:
		#删除现有的子弹，加快游戏节奏，并创建一群心的外星人
		bullets.empty()
		ai_settings.increase_speed()
		
		#提高等级
		stats.level += 1
		sb.prep_level()
		
		create_fleet(ai_settings, screen, ship, aliens)
	

def get_number_aliens_x(ai_settings, alien_width):
	"""计算每行可容纳多少外星人"""
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
	"""计算屏幕可容纳多少行外星人"""
	available_space_y = (ai_settings.screen_height - 
							(3 * alien_height) - ship_height)
	number_rows = int(available_space_y / (2 * alien_height))
	return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	# 创建一个外星人并将其加入当前行
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
	"""创建外星人群"""
	# 创建一个外星人， 并计算一行可容纳多少个外星人
	# 外星人间距为外星人宽度
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height,
					alien.rect.height)
	
	# 创建第一行外星人
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, alien_number,
				row_number)

def check_fleet_edges(ai_settings, aliens):
	"""外星人到达边缘时采取相应措施"""
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break

def change_fleet_direction(ai_settings, aliens):
	"""外星人下移，改变方向"""
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1
				

def update_aliens(ai_settings, stats, screen, ship, sb, aliens, bullets):
	"""
	检查是否有外星人位于屏幕边缘， 并更新整群外星人的位置
	"""
	check_fleet_edges(ai_settings, aliens)
	aliens.update()
	#检查外星人和飞船的碰撞
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, stats, screen, ship, sb, aliens, bullets)
	#检测是否有外星人到达底部
	check_aliens_bottom(ai_settings, stats, screen, ship, sb, aliens, bullets)

def ship_hit(ai_settings, stats, screen, ship, sb, aliens, bullets):
	"""响应被外星人撞到的飞船"""
	if stats.ships_left > 0:
		stats.ships_left -= 1
		
		#更新记分牌
		sb.prep_ships()
		
		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()
		
		#创建一群新的外星人，并将飞船放到屏幕底部
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
		
		#暂停
		sleep(0.5)
	else:
		stats.game_active = False
		#游戏结束后显示鼠标
		pygame.mouse.set_visible(True)
	
def check_aliens_bottom(ai_settings, stats, screen, ship, sb, aliens, bullets):
	"""检查是否有外星人到达屏幕底部"""
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			"""到达屏幕底部，像飞船被撞到一样处理"""
			ship_hit(ai_settings, stats, screen, ship, sb, aliens, bullets)
			break

def check_play_button(ai_settings, screen, stats, play_button, ship, sb,
	aliens, bullets, mouse_x, mouse_y):
	"""在玩家单击Play按钮时开始新游戏"""
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:
		
		#重置游戏设置
		ai_settings.initialize_dynamic_settings()
		
		#隐藏光标
		pygame.mouse.set_visible(False)
		
		#重置游戏统计信息
		stats.reset_stats()
		stats.game_active = True
		
		#重置记分牌图像
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()
		
		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()
		
		#创建一群心的外星人，并让飞船居中
		
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()

def check_high_score(stats, sb):
	"""检查是否产生了新的最高分"""
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()
