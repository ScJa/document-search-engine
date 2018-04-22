\name{read.eval}
\alias{read.eval}
\title{Read TREC Evaluation Data}
\description{\code{read.eval} is for reading in evaluation data produced by \code{trec_eval -q} and converting into a list of matrices format for R.}
\usage{read.eval(dir=".", pattern="^input.*", names)}
\arguments{
	\item{dir}{path on disk at which evaluation data is stored.}
	\item{pattern}{regex to match filenames that contain \code{trec_eval} output.  Each filename that matches the regex should be formatted the same way \code{trec_eval} output is formatted, and should have evaluation data for every topic in the evaluation (i.e. using the \code{-q} flag with \code{trec_eval}).}
	\item{names}{array of names to give to systems.  If nothing specified, the filenames will be used as the system names.  Otherwise, names in the array will be assigned to systems in the same order they are read off disk (alphanumerically w/o regard for case).}
}
\author{Ben Carterette}
\examples{
	trec8.INQ <- read.eval("/data/runs/adhoc1999/eval/", pattern="^input.INQ*", names=c("INQ601", "INQ602", "INQ603", "INQ604"))
	trec3.all <- read.eval("/data/runs/adhoc1994/eval/")
}
