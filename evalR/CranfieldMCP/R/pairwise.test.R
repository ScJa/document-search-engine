pairwise.test <- function(eval, measure="map", H="Tukey", sig.level=0.05, alternative="two.sided", test="single-step") {
#	# pre-process data
	y <- eval[[measure]]
	n <- nrow(y)
	m <- ncol(y)
	sys <- colnames(y)
	dat <- data.frame(y=as.vector(y), system=as.factor(rep(sys, each=n)), topic=as.factor(rep(1:n, m)))

	# fit linear model
	lmod <- lmer(y ~ system+(1|topic), data=dat)

	# test omnibus hypothesis
	F <- anova(lmod)[1,4]
	pval <- pf(F, n-1, m-1, lower.tail=FALSE)

	# omnibus rejected?
	if (pval < sig.level) {
		# enumerate hypotheses
		if (H[1] == "Tukey") {
			H <- outer(sys, sys, function(x,y) paste(x, "-", y))[lower.tri(matrix(0,m,m))]
		}
		if (alternative == "greater") {
			H <- paste(H, "<= 0")
		} else if (alternative == "less") {
			H <- paste(H, ">= 0")
		} else {
			H <- paste(H, "= 0")
		}
		
		res <- summary(glht(lmod, linfct=mcp(system=H)), test=adjusted(test))
	} else {
		res <- cat(paste("omnibus hypothesis not rejected (p = ", pval, ").  your systems are not statistically distinguishable!", sep=""));
	}
	res
}

