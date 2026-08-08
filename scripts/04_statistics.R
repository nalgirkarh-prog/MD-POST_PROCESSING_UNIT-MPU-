#!/usr/bin/env Rscript

# Detect systems
systems <- list.dirs("outputs", recursive = FALSE, full.names = TRUE)
systems <- systems[systems != "outputs/statistics" &
                   systems != "outputs/llm" &
                   systems != "outputs/final_report" &
                   systems != "outputs/paper"]

# Skip statistics if only one system exists
if(length(systems) < 2){
  message("Only one system detected — skipping comparative statistics.")
  quit(save="no")
}

# Create output folder
dir.create("outputs/statistics", showWarnings = FALSE, recursive = TRUE)

read_xvg <- function(path) {
  lines <- readLines(path)
  lines <- lines[!grepl("^@|^#", lines)]
  lines <- lines[lines != ""]
  if (length(lines) == 0) {
    return(NULL)
  }
  tryCatch({
    data <- read.table(text = lines)
    return(data)
  }, error = function(e) {
    return(NULL)
  })
}

metrics <- c("rmsd", "rmsf", "sasa", "hbond", "rg")
results <- data.frame()

for (metric in metrics) {
  combined <- data.frame()

  for (sys in systems) {
    sys_name <- basename(sys)
    file_path <- paste0(sys, "/", metric, "/", metric, ".xvg")

    if (file.exists(file_path)) {
      df <- read_xvg(file_path)
      if (!is.null(df) && nrow(df) > 0 && ncol(df) >= 2) {
        values <- df[, 2]
        temp <- data.frame(System=sys_name, Value=values)
        combined <- rbind(combined, temp)
      }
    }
  }

  if (nrow(combined) > 0 && length(unique(combined$System)) > 1) {
    tryCatch({
      kw <- kruskal.test(Value ~ System, data=combined)
      results <- rbind(results,
                       data.frame(Metric=metric,
                                  p_value=kw$p.value))
    }, error = function(e) {
      message(paste("Kruskal-Wallis test failed for metric:", metric))
    })
  }
}

if (nrow(results) > 0) {
  write.csv(results, "outputs/statistics/kruskal_results.csv", row.names=FALSE)
  cat("Statistics completed and saved.\n")
} else {
  cat("No statistical comparisons were performed (insufficient data).\n")
}
