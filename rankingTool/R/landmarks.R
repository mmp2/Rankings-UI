makeperm<-function(data,landmarks){
  perm=rep(0,length(landmarks)+nrow(data))
  i=1
  lmi=1
  idata=1
  #data = unlist(data)
  #newdata = c(data,landmarks)
  #newname = c(namestring,landmarks)
  #newname[rank(newdata,ties.method = )]
  for(i in 1:length(perm)){
    if(idata>length(data$ranking)){
      perm[i]=landmarks[lmi]
      lmi=lmi+1
    }else if(lmi>length(landmarks)){
      perm[i]=data$namestring[idata]
      idata=idata+1
    }else if(data$ranking[idata]<landmarks[lmi]){
      perm[i]=data$namestring[idata]
      idata=idata+1
    }else{
      perm[i]=landmarks[lmi]
      lmi=lmi+1
    }
  }
  return(perm)
}

maketest<-function(inpath, outpath, namestring, landmarks){
  rating = read.table(inpath,header=FALSE,sep=" ")
  namestring = unlist(namestring)
  emat = matrix(NA, nrow = nrow(rating), ncol = ncol(rating) + length(landmarks))

  for(dataind in 1:nrow(rating)){
    dataset = data.frame(namestring=namestring, ranking=unlist(rating[dataind,]))
    emat[dataind,] = rev(makeperm(dataset[order(dataset$ranking),],landmarks))
  }
  
  enames=c(namestring,rev(landmarks))
  
  for(i in length(enames):1){
    emat[emat==enames[i]]=i
  }

  numMatrix<-function(mat_char){
    matrix(as.numeric(mat_char),ncol = ncol(mat_char))
  }
  
  ematnum=numMatrix(emat)
  
  write.table(ematnum,paste(outpath,sep=""),col.names=FALSE,row.names=FALSE)
}

library(stringr)

readresults<-function(resultpath,landmarks,isboot=0,savepath=NA){
  efile=file(resultpath,open="r")
  edata=readLines(efile) 
  if(!isboot){
    ebest=which.max(as.numeric(edata[1:250*3]))
    ranking=edata[ebest*3-2]
    ranking=str_sub(ranking,2,-2)
    ranking=as.integer(str_split(ranking, ",")[[1]])
    ranking_vector = numeric(0)
    for(i in 1:(length(ranking))){
      ranking_vector = c(ranking_vector, as.integer(ranking[[i]]))
    }
    #real_ranking = numeric(0)
    #n = length(ranking)-length(landmarks)
    #landmarks_rank = ranking_vector[(n+1):length(ranking)]
    #for(i in 1:n){
    #  num_of_behind = sum(ranking_vector[i] > landmarks_rank)
    #  real_ranking = c(real_ranking, ranking_vector[i]-num_of_behind)
    #}
    thetas=edata[ebest*3-1]
    thetas=str_sub(thetas,2,-2)
    thetas=as.numeric(str_split(thetas, ",")[[1]])
    thetas_vector = numeric(0)
    for(i in 2:(length(thetas)-1)){
      thetas_vector = c(thetas_vector, as.numeric(thetas[[i]]))
    }
    close(efile)
    return(list(ranking_vector,thetas_vector,as.numeric(edata[ebest*3])[1]))
  }else{
    rank1 = edata[1]
    rank1 = str_sub(rank1,2,-2)
    rank1 = as.integer(str_split(rank1, ",")[[1]])
    n = length(rank1)
    mat = matrix(nr=length(edata),ncol=n-length(landmarks))
    for(j in 1:length(edata)){
      ranking=edata[j]
      ranking=str_sub(ranking,2,-2)
      ranking=as.integer(str_split(ranking, ",")[[1]])
      il = 0
      for(i in 1:n){
        if(ranking[[i]] >= n-length(landmarks)){
          il = il + 1
        }else{
          mat[j,i-il] = as.integer(ranking[[i]])
        }
      }
    }
    close(efile)
    write.table(mat,file=savepath,sep=",",row.names=FALSE, col.names=FALSE)
  }
}

