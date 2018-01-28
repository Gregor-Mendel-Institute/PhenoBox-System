package at.gmi.djamei.r;

import org.apache.commons.vfs2.FileName;
import org.apache.commons.vfs2.FileSystemException;
import org.apache.commons.vfs2.NameScope;
import org.apache.commons.vfs2.impl.DefaultFileSystemManager;

public class RestrictedFileSystemManager extends DefaultFileSystemManager {
	private String renjinBasePath;
	private String workingDirectory;

    public RestrictedFileSystemManager(String renjinBasePath, String workingDirectory) {
        super();
        this.renjinBasePath = renjinBasePath;
        this.workingDirectory = workingDirectory;
    }
    /**
     * Resolves a name, relative to the file. If the supplied name is an absolute path, then it is resolved relative to
     * the root of the file system that the file belongs to. If a relative name is supplied, then it is resolved
     * relative to this file name.
     *
     * @param root The base FileName.
     * @param path The path to the file relative to the base FileName or an absolute path.
     * @return The constructed FileName.
     * @throws FileSystemException if an error occurs constructing the FileName.
     */
    @Override
    public FileName resolveName(final FileName root, final String path) throws FileSystemException {
    	//A Renjin session is first created with a default path and so it needs access to this directory for initialization
    	//The second condition is needed to change the working directory of the session with an absolute path
    	 if (root.getPath().equals(renjinBasePath) || (root.getPath().equals(workingDirectory)&& path.equals("/"))) {
             return resolveName(root, path, NameScope.FILE_SYSTEM);
         } else {//All other relative paths have to be a descendentes or the root itself of the VFS
             return resolveName(root, path, NameScope.DESCENDENT_OR_SELF);
         }
    }

}

