# lab01
# variables
health = 50
damage = 0
block = False

states = ['Attacking', 'Defending', 'Healing']
current_state = 'Attacking'

game_time = 0
running = True
max_running = 10

while running :
    game_time += 1
    print("Current Health:", health)
    print("Damage Taken:", damage)

    if current_state is 'Attacking' :
        print("Attacking the player...")
        health -= 5

        current_state = 'Defending'

    elif current_state is 'Defending' :
        print("Blocking incoming damage...")
        block = True

        if block is True :
            print("Damage Blocked!")
            damage += 5
            health -= 5
            current_state = 'Attacking'

    elif current_state is 'Healing' :
        print("Healing...")
        health += 10

        current_state = 'Defending'

    elif health < 10 :
        current_state = 'Healing'

        damage += 5
        health += 5
        print("Healing...")

    #if broken
    else :
        print("Broken!")
        die()

    #end game
    if game_time > max_running :
        running = False
        break

    elif health < 0 :
        running = False
        break

# tell player the game has ended
print("Game Ended")
