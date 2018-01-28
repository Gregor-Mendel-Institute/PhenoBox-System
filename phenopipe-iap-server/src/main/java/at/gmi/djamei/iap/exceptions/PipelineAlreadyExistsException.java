package at.gmi.djamei.iap.exceptions;

import org.bson.types.ObjectId;

public class PipelineAlreadyExistsException extends Exception {

	private static final long serialVersionUID = 8247359378851484317L;
	final String pipelineName;
	final String author;
	final ObjectId existingId;
	public PipelineAlreadyExistsException(String pipelineName, String author, ObjectId existingId) {
        this(pipelineName, author, existingId, "A pipeline with the name "+pipelineName+" by "+author+" already exists. (ID: "+existingId.toHexString()+")");
    }
	public PipelineAlreadyExistsException(String pipelineName, String author, ObjectId existingId,String message) {
        this(pipelineName, author, existingId,message,null);     
    }
	public PipelineAlreadyExistsException(String pipelineName, String author, ObjectId existingId, Throwable cause) {
        this(pipelineName, author, existingId, "A pipeline with the name "+pipelineName+" by "+author+" already exists. (ID: "+existingId.toHexString()+")", cause);
    }
	public PipelineAlreadyExistsException(String pipelineName, String author, ObjectId existingId, String message,Throwable cause) {
        super(message, cause);
        this.pipelineName=pipelineName;
        this.author=author;
        this.existingId=existingId;
    }
	public String getPipelineName(){
		return pipelineName;
	}
	public ObjectId getId(){
		return existingId;
	}
	public String getAuthor(){
		return author;
	}
}
