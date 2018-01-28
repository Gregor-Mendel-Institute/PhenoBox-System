package at.gmi.djamei.iap;

import org.bson.types.ObjectId;

public class IAPPipeline {
	final ObjectId id;
	String name;
	String description;
	String author;
	String tunedForVersion;
	String source;
	
	public IAPPipeline(ObjectId id, String name, String description, String author, String tunedForVersion, String source) {
		super();
		this.id = id;
		this.name = name;
		this.description = description;
		this.author = author;
		this.tunedForVersion = tunedForVersion;
		this.source = source;
	}

	public ObjectId getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getAuthor() {
		return author;
	}

	public void setAuthor(String author) {
		this.author = author;
	}

	public String getTunedForVersion() {
		return tunedForVersion;
	}

	public void setTunedForVersion(String tunedForVersion) {
		this.tunedForVersion = tunedForVersion;
	}

	public String getSource() {
		return source;
	}

	public void setSource(String source) {
		this.source = source;
	}
	
	
}
