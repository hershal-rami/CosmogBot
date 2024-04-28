-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema MBTL_STATS_DB
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema MBTL_STATS_DB
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `MBTL_STATS_DB` DEFAULT CHARACTER SET utf8 ;
USE `MBTL_STATS_DB` ;

-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`PKMN_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`PKMN_Stats` (
  `pkmn_id` INT NOT NULL,
  `type1` VARCHAR(45) NULL,
  `type2` VARCHAR(45) NULL,
  `HP` VARCHAR(45) NULL,
  `ATK` VARCHAR(45) NULL,
  `DEF` VARCHAR(45) NULL,
  `SPATK` VARCHAR(45) NULL,
  `SPDEF` VARCHAR(45) NULL,
  `SPE` VARCHAR(45) NULL,
  `pkmn_name` VARCHAR(45) NULL,
  PRIMARY KEY (`pkmn_id`),
  UNIQUE INDEX `pkmn_id_UNIQUE` (`pkmn_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Player_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Player_Stats` (
  `p_id` INT NOT NULL,
  `p_name` VARCHAR(45) NULL,
  `p_wins` INT NULL,
  `p_losses` INT NULL,
  `p_diff` INT NULL,
  `p_post_season_w` INT NULL,
  `p_post_season_l` INT NULL,
  `p_championships` INT NULL,
  PRIMARY KEY (`p_id`),
  UNIQUE INDEX `p_id_UNIQUE` (`p_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Poke_Move_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Poke_Move_Stats` (
  `pms_pkmn_id` INT NOT NULL,
  `pms_move` VARCHAR(45) NOT NULL,
  `pms_times_used` INT NOT NULL,
  PRIMARY KEY (`pms_pkmn_id`, `pms_move`),
  CONSTRAINT `pkmn_move_id`
    FOREIGN KEY (`pms_pkmn_id`)
    REFERENCES `MBTL_STATS_DB`.`PKMN_Stats` (`pkmn_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Poke_Player_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Poke_Player_Stats` (
  `pps_coach_id` INT NOT NULL,
  `pps_pkmn_id` INT NOT NULL,
  `pps_season` INT NOT NULL,
  `pps_kills` INT NOT NULL,
  `pps_deaths` INT NOT NULL,
  `pps_dmg_dealt` INT NOT NULL,
  `pps_dmg_taken` INT NOT NULL,
  `pps_times_switched` INT NOT NULL,
  `pps_pkmn_poisoned` INT NOT NULL,
  `pps_crits` INT NOT NULL,
  `pps_rocks_spikes_set` INT NOT NULL,
  `pps_wins` INT NOT NULL,
  `pps_losses` INT NOT NULL,
  `pps_diff` INT NOT NULL,
  PRIMARY KEY (`pps_coach_id`, `pps_pkmn_id`, `pps_season`),
  CONSTRAINT `pkmn_id`
    FOREIGN KEY (`pps_pkmn_id`)
    REFERENCES `MBTL_STATS_DB`.`PKMN_Stats` (`pkmn_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `pps_p_id`
    FOREIGN KEY (`pps_coach_id`)
    REFERENCES `MBTL_STATS_DB`.`Player_Stats` (`p_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Matchup_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Matchup_Stats` (
  `p_id_1` INT NOT NULL,
  `p_id_2` INT NOT NULL,
  `p1_wins` INT NULL,
  `p2_wins` INT NULL,
  `p1_diff` INT NULL,
  PRIMARY KEY (`p_id_1`, `p_id_2`),
  CONSTRAINT `p_id_1`
    FOREIGN KEY (`p_id_1`)
    REFERENCES `MBTL_STATS_DB`.`Player_Stats` (`p_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `p_id_2`
    FOREIGN KEY (`p_id_2`)
    REFERENCES `MBTL_STATS_DB`.`Player_Stats` (`p_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Div_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Div_Stats` (
  `div_id` INT NOT NULL,
  `games_played` INT NULL,
  `div_name` VARCHAR(45) NULL,
  PRIMARY KEY (`div_id`),
  UNIQUE INDEX `div_id_UNIQUE` (`div_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MBTL_STATS_DB`.`Poke_Div_Stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MBTL_STATS_DB`.`Poke_Div_Stats` (
  `pds_div_id` INT NOT NULL,
  `pds_pkmn_id` INT NOT NULL,
  `pds_season` INT NOT NULL,
  `pds_kills` INT NOT NULL,
  `pds_deaths` INT NOT NULL,
  `pds_dmg_dealt` INT NOT NULL,
  `pds_dmg_taken` INT NOT NULL,
  `pds_times_switched` INT NOT NULL,
  `pds_pkmn_poisoned` INT NOT NULL,
  `pds_crits` INT NOT NULL,
  `pds_rocks_spikes_set` INT NOT NULL,
  `pds_wins` INT NOT NULL,
  `pds_losses` INT NOT NULL,
  `pds_diff` INT NOT NULL,
  PRIMARY KEY (`pds_div_id`, `pds_pkmn_id`, `pds_season`),
  CONSTRAINT `div_id`
    FOREIGN KEY (`pds_div_id`)
    REFERENCES `MBTL_STATS_DB`.`Div_Stats` (`div_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `pds_pkmn_id`
    FOREIGN KEY (`pds_pkmn_id`)
    REFERENCES `MBTL_STATS_DB`.`PKMN_Stats` (`pkmn_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
