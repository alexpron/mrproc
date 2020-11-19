"""

"""

from nipype.interfaces import fsl
import nipype.pipeline.engine as pe

def create_rigid_registration_node():
    """

    :return:
    """
    #Ensure rigid + homogenous scaling deformation, default cost
    rigid_registration = pe.Node(fsl.FLIRT(dof=7), name='rigid_registration')
    rigid_registration.inputs.output_type = "NIFTI_GZ"
    return rigid_registration

