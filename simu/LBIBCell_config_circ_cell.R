setwd(getwd())


# parameters:

LX   = 1000  # domain size x
LY   = 1000  # domain size y
DIA  = 100
R    = DIA/2  # radius 
MIDX = LX * 1/4 # midpoint of the box
MIDY = LY * 3/4 # midpoint of the box
RES  = 360  # angular resolution
ID   = 1

# Declare geometry point matrix
NODES <- matrix(NA,nrow=0,ncol = 3) 

# Create PhysicalNodes #Nodes (id xPos yPos)

phi <- seq(2*pi, 0, -2*pi/RES)
for (i in phi) {
  xpos <- MIDX + R*sin(i)
  ypos <- MIDY + R*cos(i)
  NODES <- rbind(NODES, c(ID,xpos,ypos))
  ID <- ID + 1
}

# create Connections #Connection (nodeId1 nodeId2 domainId bsolver cdesolver ...)

# Name your solvers
solver1 <- 'BoundarySolverNoFluxD2Q5'
solver2 <- 'tutorial_02_CDESolverD2Q5_R'



# Declare connection point matrix
CONNECTIONS <- matrix(NA,nrow=0,ncol = 3) 

COUNT <- matrix(1,ncol=1)
for (i in 1:(nrow(NODES)-1)) {
  CONNECTIONS <- rbind(CONNECTIONS, c(COUNT,COUNT+1,1))
  COUNT <- COUNT+1
}

CONNECTIONS <- rbind(CONNECTIONS, c(COUNT,1,1)) # Close connection at last column

CONNECTIONS <- cbind(CONNECTIONS,NA,NA,NA) # optionally add solver1,... instead of the NAs

colnames(NODES) <- c("#Nodes (id","xPos","yPos)") 
colnames(CONNECTIONS) <- c("#Connection (nodeId1","nodeId2","domainId","bsolver","cdesolver","...)") 

#write to file:



write.table(NODES, file ="geometry_1000box_DIA100_upper_left.txt",  append = T, quote = F, sep = "\t", row.names = F, na="");
write.table(CONNECTIONS, file ="geometry_1000box_DIA100_upper_left.txt",  append = T, quote = F, sep = "\t", row.names = F, na="")

