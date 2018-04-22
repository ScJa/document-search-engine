\name{pairwise.test}
\alias{pairwise.test}
\title{Simultaneous Pairwise Tests for IR Evaluation}
\description{\code{pairwise.test} is for testing multiple hypotheses about differences between IR systems simultaneously.  First it tests the omnibus hypothesis that all the systems are equivalent; if that is rejected, it tests the specified list of hypotheses and performs p-value adjustment.}
\usage{pairwise.test(eval, measure="map", H="Tukey", sig.level=0.05, alternative="two.sided", test="single-step")}
\arguments{
	\item{eval}{a list of matrices containing system-topic evaluation data.  Produced by \code{read.eval}.}
	\item{measure}{the effectiveness measure to test.  Must be one of the ones reported by \code{trec_eval}.}
	\item{H}{the list of hypotheses to test.  Use "Tukey" to perform all pairwise tests.  Otherwise, specify a hypothesis with the character string "S1 - S2".}
	\item{sig.level}{the significance level to test the omnibus hypothesis.}	\item{alternative}{one of "two.sided", "greater", or "less".}
	\item{test}{the type of p-value adjustment to perform.  Can be anything accepted by \code{p.adjust} or \code{summary.glht}.}
}
\author{Ben Carterette}
\examples{
	trec8.INQ <- read.eval("/data/runs/adhoc1999/eval", pattern="^input.INQ*", names=c("INQ601","INQ602","INQ603","INQ604"))
	pairwise.test(trec8.INQ, "map", H="Tukey")
	pairwise.test(trec8.INQ, "map", H=c("INQ601 - INQ602", "INQ602 - INQ603", "INQ603 - INQ604"), alternative="greater")
}
