library(stringr)
library(plotrix)
library(latex2exp)
library(Rcpp)

doit<-function(test,depth,shift,thetas,invert=FALSE,thetaval=1){
  lps=gregexpr(pattern="\\(",test)[[1]]
  rps=gregexpr(pattern="\\)",test)[[1]]
  commas=gregexpr(pattern="\\,",test)[[1]]
  pipes=gregexpr(pattern="\\|",test)[[1]]
  n=length(pipes)+1
  #print("hello")
  #print(depth)
  if(pipes[1]!=-1){
    ind=1
    while(sum(lps<commas[ind])-1!=sum(rps<commas[ind]))
      ind=ind+1
    lhs=substr(test,2,commas[ind]-1)
    nl=length(gregexpr(pattern="\\|",lhs)[[1]])+1
    if(gregexpr(pattern="\\|",lhs)[[1]][1]==-1)
      nl=1
    rhs=substr(test,commas[ind]+1,pipes[length(pipes)]-1)
    nr=length(gregexpr(pattern="\\|",rhs)[[1]])+1
    if(gregexpr(pattern="\\|",rhs)[[1]][1]==-1)
      nr=1
    tstr=substr(test,pipes[length(pipes)]+2,str_length(test)-2)
    thet=as.double(strsplit(tstr,";")[[1]])
    if(invert & thet[thetaval]<0){
      rmat=matrix(c(-1,depth,shift,n,nr,nl,-thet),nrow=1)
      rmat=rbind(rmat,doit(rhs,depth+1,shift,thetas,invert,thetaval))
      rmat=rbind(rmat,doit(lhs,depth+1,shift+nr,thetas,invert,thetaval))
    }
    else{
      rmat=matrix(c(-1,depth,shift,n,nl,nr,thet),nrow=1)
      rmat=rbind(rmat,doit(lhs,depth+1,shift,thetas,invert,thetaval))
      rmat=rbind(rmat,doit(rhs,depth+1,shift+nl,thetas,invert,thetaval))
    }
    return(rmat)
  }
  else{
    #print(paste("Leaf",test))
    rmat=matrix(c(as.integer(test),depth,shift,1,0,0,rep(0,thetas)),nrow=1)
  }
}

plotTree<-function(inMatrix){
  plot(c(0,max(inMatrix[,3])+1),c(0,min(-inMatrix[,2]/2)),type='n')
  for(i in 1:dim(inMatrix)[1]){
    if(inMatrix[i,1]==-1){
      lines(c(rep(inMatrix[i,3]+inMatrix[i,5]/2,2),rep(inMatrix[i,3]+inMatrix[i,4]-inMatrix[i,6]/2,2)),-inMatrix[i,2]/2-c(1/2,0,0,1/2))
      mid=(inMatrix[i,3]+inMatrix[i,5]/2+inMatrix[i,3]+inMatrix[i,4]-inMatrix[i,6]/2)/2
      label=as.character(round(inMatrix[i,7],3))
      if(dim(inMatrix)[2]>7)
        for(j in 2:(dim(inMatrix)[2]-6))
          label=paste(label,as.character(round(inMatrix[i,6+j],3)),sep="\n")
      boxed.labels(mid,-inMatrix[i,2]/2,labels=label,ypad=1.3,xpad=1.3,cex=.6)
    }
    else{
      boxed.labels(inMatrix[i,3]+.5,-inMatrix[i,2]/2,labels=as.character(inMatrix[i,1]),ypad=1.3,xpad=1.3,cex=1.1)
    }
  }
}

probFromExp<-function(theta){
  exp(-(theta)) / (1 + exp(-(theta)));
}




plotLimitedTree<-function(inMatrix,k,colors,title="None",type=2,itemStr=NULL){
  plot(c(0,max(inMatrix[,3])+1),c(-.5,min(-inMatrix[,2]/2)),type='n', xaxt='n', yaxt='n', bty = 'n',main=title,xlab='',ylab='', mar=c(0,0,0,0))
  for(i in 1:dim(inMatrix)[1]){
    if(inMatrix[i,1]==-1){
      lines(c(rep(inMatrix[i,3]+inMatrix[i,5]/2,2),rep(inMatrix[i,3]+inMatrix[i,4]-inMatrix[i,6]/2,2)),-inMatrix[i,2]/2-c(1/2,0,0,1/2),lwd=2)
      mid=(inMatrix[i,3]+inMatrix[i,5]/2+inMatrix[i,3]+inMatrix[i,4]-inMatrix[i,6]/2)/2
      theta=inMatrix[i,6+k]
      prob=probFromExp(theta)
      color=rgb(prob,0,1-prob)
      if(type==1)
        label=as.character(round(probFromExp(inMatrix[i,6+k]),3))
      if(type==2)
        label=as.character(round(inMatrix[i,6+k],3))
      if(type==3)
        label=as.character(round(exp(-inMatrix[i,6+k]),3))
      boxed.labels(mid,-inMatrix[i,2]/2,labels=label,ypad=1.3,xpad=1.3,cex=1.2,bg=color,lwd=2)
    }
    else if(is.null(itemStr)){
      boxed.labels(inMatrix[i,3]+.5,-inMatrix[i,2]/2,labels=as.character(inMatrix[i,1]),bg=colors[inMatrix[i,1]+1], ypad=1.5,xpad=1.3,cex=1.2,lwd=2)
    }
    else{
      boxed.labels(inMatrix[i,3]+.5,-inMatrix[i,2]/2,labels=itemStr[inMatrix[i,1]+1],bg=colors[inMatrix[i,1]+1], ypad=1.5,xpad=1.3,cex=1.2,lwd=2)
    }
  }
}


makeplot = function(namePlot, isplot, tree, rankingnames){
  testmat = doit(tree, 1, 0, 1)
  if(isplot){
    dimPlot = c(1,1)*50
    unit    = c(7,9)
    png(namePlot, height=dimPlot[1]*unit[1], width=dimPlot[2]*unit[2],pointsize = 12)
    par(mar=c(0.1,0.1,0.1,0.1),mfrow=c(1,1),bg=NA)
    plotLimitedTree(testmat,1,colors=rep("azure",length(rankingnames)),type=2,title="",itemStr=rankingnames)
    dev.off()
  }
  return(testmat[(testmat[,1]!=-1),1])
}


makematrix = function(mat){
  n = nrow(mat)
  mat = rbind(mat[mat[,4]!=1,], mat[mat[,4]==1,])
  n1 = nrow(mat[mat[,4]!=1,])
  res = matrix(data=NA, nrow=n, ncol=5)
  for(i in (n1+1):n){
    res[i,1] = 0
    res[i,2] = 0
    res[i,3] = 1
    res[i,4] = 0
    res[i,5] = mat[i,1]
  }
  res[(n1+1):n,] = res[order(mat[(n1+1):n,2])+n1,]
  j = 0
  for(i in 1:n1){
    if(mat[i,5]>1){
      res[i,1] = match(mat[i,5],mat[,4])-1
      mat[res[i,1]+1,4] = NA 
    }else{
      res[i,1] = j + n1
      j = j+1
    }
    if(mat[i,6]>1){
      res[i,2] = match(mat[i,6],mat[,4])-1
      mat[res[i,2]+1,4] = NA 
    }else{
      res[i,2] = j + n1
      j = j+1
    }
    res[i,3] = 0
    res[i,4] = mat[i,7]
    res[i,5] = 0
  }
}

makedata = function(n, Bsamples){
  testmat = doit(tree, 1, 0, 1)
  treeAsMat = makematrix(testmat)
  rRIM(Bsamples, treeAsMat)
}
    






