from network.ActivationFunctions import ActivationFunctions as af



"""Class for reading a genome from a file
For reference read: Stanley, K.O., Miikkulainen, R., (2001). Evolving Neural Networks through Augmenting Topologies"""
class GenomeReader:
    def __init__(self,model):
        self.model = model

    #read genome from a file
    def makeGenome(self, genome_path):
        #first construct input and output neurons, these are always the same and are not included in the genome
        n_genes = [NGene(i,af.SIGMOID) for i in range(0,65)]
        for i in range(274,288): n_genes.append(NGene(i,af.SIGMOID))
        c_genes = []
        with open(genome_path,'r') as f:
            #read links from file.
            for line in f:
                data = (line.rstrip()).split(':')
                innov = int(data[0])
                in_id = int(data[1])
                ou_id = int(data[2])
                weigh = float(data[3])
                enabl = (data[4] == '1')
                c_genes.append( CGene( in_id, ou_id, weigh, enabl, innov ) )

                #if a link goes to or comes from a hidden node that is not yet in the genome, add to the genome
                if len(list(filter (lambda n: n.getId() == in_id, n_genes))) == 0:
                    n_genes.append( NGene(in_id, af.SIGMOID) )
                if len(list(filter (lambda n: n.getId() == ou_id, n_genes))) == 0:
                    n_genes.append( NGene(ou_id, af.SIGMOID) )
        #sort nodes on id for consistent execution order
        n_genes.sort(key=lambda n: n.getId())
        return Genome( n_genes, c_genes )    

"""Genome class containing both the nodes and link genes of an individual"""
class Genome:
    def __init__(self, n_genes, c_genes):
        self.n_genes = n_genes
        self.c_genes = c_genes

    def getNgenes(self):
        return self.n_genes

    def getCgenes(self):
        return self.c_genes

"""Node gene, contains the id (ie. location) of a node and the activation method used by that node"""
class NGene:
    def __init__(self, n_id, method):
        self.n_id     = n_id
        self.method   = method

    def getId(self):
        return self.n_id

    def getMethod(self):
        return self.method

"""Link gene, contains the ids of in and out nodes, the weight of the link, whether it is enabled and the innovation number"""
class CGene:
    def __init__(self, in_id, out_id, weight, enabled, innov):
        self.in_id   = in_id
        self.out_id  = out_id
        self.weight  = weight
        self.enabled = enabled
        self.innov   = innov


    def getCopy(self):
        return CGene( self.in_id,
                      self.out_id,
                      self.weight,
                      self.enabled,
                      self.innov )

    """GETTER METHODS"""
    def getIn(self):
        return self.in_id

    def getOut(self):
        return self.out_id

    def getWeight(self):
        return self.weight

    def getEnabled(self):
        return self.enabled

    def getInnov(self):
        return self.innov

    """SETTER METHODS"""
    def setWeight(self, new_val):
        self.weight = new_val

    def setEnabled(self, new_val):
        self.enabled = new_val
