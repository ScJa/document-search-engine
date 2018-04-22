read.eval <- function(dir=".", pattern="^input.*", names=NULL)
{
	evals <- list()
	files <- dir(dir, pattern)
	for (i in 1:length(files)) {
		res <- read.table(paste(dir, "/", files[i], sep=""), header=FALSE)
		res <- res[-which(res$V2=="all"),]
		if (!is.null(names)) {
			evals[[names[i]]] <- res
		} else {
			evals[[files[i]]] <- res
		}
	}
	
	measures <- unique(evals[[1]]$V1)
	ret <- lapply(measures, function(m) sapply(evals, function(x) x$V3[x$V1==m]))

	names(ret) <- measures
	ret
}
