from numpy import dot,cross,matrix

# pyNastran
from elements import Element
from pyNastran.general.generalMath import Area

def Volume4(n1,n2,n3,n4):
    """
    V = (a-d) * ((b-d) x (c-d))/6   where x is cross and * is dot
    \f[ \large V = {(a-d) \dot \left( (b-d) \times (c-d) \right) }{6} \f]
    """
    V = dot((n1-n4),cross(n2-n4,n3-n4))/6.
    return V

class SolidElement(Element):
    def __init__(self,card,data):
        Element.__init__(self,card,data)

    def crossReference(self,mesh):
        self.nodes = mesh.Nodes(self.nodes)
        self.pid   = mesh.Property(self.pid)

    def Mass(self):
        return self.Rho()*self.Volume()
    
    def Rho(self):
        return self.pid.mid.rho

    def isSameCard(self,elem):
        if self.type!=elem.type:  return False
        fields1 = [self.eid,self.Pid()]+self.nodes
        fields2 = [elem.eid,elem.Pid()]+elem.nodes
        return self.isSameFields(fields1,fields2)

    def rawFields(self):
        fields = [self.type,self.eid,self.Pid()]+self.nodeIDs()
        return fields

class CHEXA8(SolidElement):
    """
    CHEXA EID PID G1 G2 G3 G4 G5 G6
    G7 G8
    """
    type = 'CHEXA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)
        if card:
            #print "hexa = ",card
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,11)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids     = data[2:]
            assert len(data)==10,'len(data)=%s data=%s' %(len(data),data)
        #print "nids = ",nids
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==8

    def areaCentroid(self,n1,n2,n3,n4):
        a = n1-n2
        b = n2-n4
        area1 = Area(a,b)
        c1 = (n1+n2+n4)/3.

        a = n2-n4
        b = n2-n3
        area2 = Area(a,b)
        c2 = (n2+n3+n4)/3.
        
        area = area1+area2
        centroid = (c1*area1+c2*area2)/area
        return(area,centroid)

    def Centroid(self):
        (n1,n2,n3,n4,n5,n6,n7,n8) = self.nodePositions()
        A1,c1 = self.areaCentroid(n1,n2,n3,n4)
        A2,c2 = self.areaCentroid(n5,n6,n7,n8)
        c = (c1+c2)/2.
        return c

    def Volume(self):
        (n1,n2,n3,n4,n5,n6,n7,n8) = self.nodePositions()
        A1,c1 = self.areaCentroid(n1,n2,n3,n4)
        A2,c2 = self.areaCentroid(n5,n6,n7,n8)
        V = (A1+A2)/2.*(c1-c2)
        return abs(V)

class CHEXA20(CHEXA8):
    """
    CHEXA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10 G11 G12 G13 G14
    G15 G16 G17 G18 G19 G20
    """
    type = 'CHEXA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)

        if card:
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,23)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids     = data[2:]
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        msg = 'len(nids)=%s nids=%s' %(len(nids),nids)
        assert len(self.nodes)<=20,msg

    def Centroid(self):
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15,n16,n17,n18,n19,n20) = self.nodePositions()
        A1,c1 = self.areaCentroid(n1,n2,n3,n4)
        A2,c2 = self.areaCentroid(n5,n6,n7,n8)
        c = (c1+c2)/2.
        return c

    def Volume(self):
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15,n16,n17,n18,n19,n20) = self.nodePositions()
        A1,c1 = self.areaCentroid(n1,n2,n3,n4)
        A2,c2 = self.areaCentroid(n5,n6,n7,n8)
        V = (A1+A2)/2.*(c1-c2)
        return abs(V)


class CPENTA6(SolidElement):
    """
    CPENTA EID PID G1 G2 G3 G4 G5 G6
      *----------*
     / \        / \
    / A \      / c \
    *---*-----*-----*
    V = (A1+A2)/2  * (c1-c2)
    C = (c1-c2)/2
    """
    type = 'CPENTA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)

        if card:
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,9)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids     = data[2:]
            assert len(data)==8,'len(data)=%s data=%s' %(len(data),data)
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==6

    def Centroid(self):
        n = self.nodePositions()
        (n1,n2,n3,n4,n5,n6) = n
        c1 = (n1+n2+n3)/3.
        c2 = (n4+n5+n6)/3.
        c = (c1+c2)/2.
        return c

    def Volume(self):
        n = self.nodePositions()
        (n1,n2,n3,n4,n5,n6) = n
        A1 = Area(n3-n1,n2-n1)
        A2 = Area(n6-n4,n5-n4)
        c1 = (n1+n2+n3)/3.
        c2 = (n4+n5+n6)/3.
       
        V = (A1+A2)/2. * (c1-c2)
        return abs(V)

class CPENTA15(CPENTA6):
    """
    CPENTA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10 G11 G12 G13 G14
    G15
    """
    type = 'CPENTA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)

        if card:
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,18)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids = data[2:]
            assert len(data)==17,'len(data)=%s data=%s' %(len(data),data)
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        assert len(self.nodes)<=15

    def Centroid(self):
        n = self.nodePositions()
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15) = n
        c1 = (n1+n2+n3)/3.
        c2 = (n4+n5+n6)/3.
        c = (c1-c2)/2.
        return c

    def Volume(self):
        n = self.nodePositions()
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15) = n
        A1 = Area(n3-n1,n2-n1)
        A2 = Area(n6-n4,n5-n4)
        c1 = (n1+n2+n3)/3.
        c2 = (n4+n5+n6)/3.
       
        V = (A1+A2)/2. * (c1-c2)
        return abs(V)

class CTETRA4(SolidElement):
    """
    CTETRA EID PID G1 G2 G3 G4
    """
    type = 'CTETRA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)
        if card:
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,7)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids = data[2:]
            assert len(data)==6,'len(data)=%s data=%s' %(len(data),data)
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==4

    def Volume(self):
        (n1,n2,n3,n4) = self.nodePositions()
        return Volume4(n1,n2,n3,n4)

    def Centroid(self):
        (n1,n2,n3,n4) = self.nodePositions()
        return (n1+n2+n3+n4)/4.

    def Jacobian(self):
        """
        \f[ \large   [J] = 
          \left[
          \begin{array}{ccc}
              1   & 1   & 1   \\
              x_1 & y_1 & z_1 \\
              x_2 & y_2 & z_2 \\
              x_3 & y_3 & z_3 \\
              x_4 & y_4 & z_4 \\
          \end{array} \right]
        \f]
         @todo
            this has got to be wrong
         @warning
            this has got to be wrong
        """
        m = matrix((6,6),'d')
        m[0][0] = m[0][1] = m[0][2] = m[0][2] = 1.
        m[1][0]=n1[0]; m[2][0]=n1[1]; m[3][0]=n1[2];
        m[1][1]=n2[0]; m[2][1]=n2[1]; m[3][1]=n2[2];
        m[1][2]=n3[0]; m[2][2]=n3[1]; m[3][2]=n3[2];
        m[1][3]=n4[0]; m[2][3]=n4[1]; m[3][3]=n4[2];
        return m

class CTETRA10(CTETRA4):
    """
    CTETRA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10
    CTETRA   1       1       239     229     516     99      335     103
             265     334     101     102
    """
    type = 'CTETRA'
    def __init__(self,card=None,data=None):
        SolidElement.__init__(self,card,data)
        if card:
            self.eid = card.field(1)
            self.pid = card.field(2)
            nids = card.fields(3,13)
        else:
            self.eid = data[0]
            self.pid = data[1]
            nids = data[2:]
            assert len(data)==12,'len(data)=%s data=%s' %(len(data),data)
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        assert len(self.nodes)<=10

    def Volume(self):
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10) = self.nodePositions()
        return Volume4(n1,n2,n3,n4)

    def Centroid(self):
        (n1,n2,n3,n4,n5,n6,n7,n8,n9,n10) = self.nodePositions()
        return (n1+n2+n3+n4)/4.
