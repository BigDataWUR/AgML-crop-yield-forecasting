if (!require("pacman")) install.packages("pacman")
pacman::p_load(rnassqs, tidyverse)

api_key = readLines("nass_api.txt", warn = F) #Modify "nass_api.txt" to provide your api file.
nassqs_auth(key = api_key)

#Add more commodities here. Should match the Commodity field in NASS QuickStats.
commodities <- c("CORN" ,"WHEAT")

#Add more "types" of crops here, e.g. "WHEAT, SPRING" for spring wheat or "WHEAT" for all types of wheat combined.
crops <- c("CORN, GRAIN", "WHEAT, WINTER")

years <- 2000:2022

nass_data_items <- c(paste0(crops, " - ACRES HARVESTED"),
                     paste0(crops, " - YIELD, MEASURED IN BU / ACRE"),
                     paste0(crops, " - PRODUCTION, MEASURED IN BU"))

get_params <- function(data_item){
  params <- list(
  source_desc = "SURVEY",
  commodity_desc = commodities,
  domaincat_desc="NOT SPECIFIED",
  agg_level_desc = "COUNTY",
  year = years,
  short_desc = data_item
)
}

# Testing the function
# test <- get_params(nass_data_items[1])
# nassqs_record_count(test) # Counting records because NASS only allows 50k records at a time.
# test2 <- nassqs(test)

get_items <- map(nass_data_items, get_params)

raw_data <- map_dfr(get_items, nassqs)

old_names <-  c("year", "state_name", "county_name", 
                "YIELD, MEASURED IN BU / ACRE", "ACRES HARVESTED", 
                "PRODUCTION, MEASURED IN BU", "state_fips_code", "county_code")
new_names <- c("Year", "State", "County", "Yield", "Area", "Production", "statefp", "countyfp")

select_stats <- raw_data |> 
  select('year', 'state_name', 'county_name', 'Value', 'state_fips_code', 'county_code', 'short_desc') |> 
  filter(county_name != "OTHER (COMBINED) COUNTIES") |>
  type_convert() |> 
  separate(short_desc, c("Crop", "Var_name"), "- ") |> 
  mutate(Crop = map_chr(str_split(tolower(Crop), ", "), ~paste0((.), collapse = "_"))) |> 
  pivot_wider(names_from="Var_name", values_from=c("Value")) |> 
  rename_with(~ new_names, all_of(old_names))

write_csv(select_stats, "datasets/nass_stats.csv")


