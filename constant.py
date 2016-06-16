START_MONEY = 10000  # initial money
PLAYER_NO = 2  # player number
ROW_OF_REGIONS = 8 # number of regions in a row
COLUMN_OF_REGIONS = 8 # number of regions in a column
TOTAL_REGIONS = ((ROW_OF_REGIONS - 1) + (COLUMN_OF_REGIONS - 1)) * 2  # number of total regions
MAXIMUM_TURN = 20  # game's maximum turn
STOP_TURN = 1  # stop turn when arrive at desert
SALARY = 2000  # salary when pass starting point
TOLL_RATE = 1  # toll price ratio with region price
UPGRADE_RATE = 1.25  # upgrade price ratio with region price
CHANGE_OWNER_RATE = 1.4  # change owner price ration with region price

REGION_FIRST_BUY = 1  # when region is purchased first time
REGION_CHANGE_OWNER = 2  # when owner is changed
REGION_UPGRADE = 3  # when region is upgraded

# ask messages
ASK_BUY_MESSAGE = {
    REGION_FIRST_BUY: "Do you want buy this region?($%d)",
    REGION_CHANGE_OWNER: "Do you want to buy this region?($%d)",
    REGION_UPGRADE: "Do you want to upgrade this region?($%d)",
}

REGION_OF_X_POS = [0 for i in range(ROW_OF_REGIONS - 1)] + [i for i in range(COLUMN_OF_REGIONS - 1)] + [COLUMN_OF_REGIONS - 1 for i in range(ROW_OF_REGIONS - 1)] + [(COLUMN_OF_REGIONS - 1 - i) for i in range(COLUMN_OF_REGIONS - 1)]
REGION_OF_Y_POS = [i for i in range(ROW_OF_REGIONS - 1)] + [ROW_OF_REGIONS - 1 for i in range(COLUMN_OF_REGIONS - 1)] + [(ROW_OF_REGIONS - 1 - i) for i in range(ROW_OF_REGIONS - 1)] + [0 for i in range(COLUMN_OF_REGIONS - 1)]
