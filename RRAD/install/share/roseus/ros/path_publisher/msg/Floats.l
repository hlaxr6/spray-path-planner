;; Auto-generated. Do not edit!


(when (boundp 'path_publisher::Floats)
  (if (not (find-package "PATH_PUBLISHER"))
    (make-package "PATH_PUBLISHER"))
  (shadow 'Floats (find-package "PATH_PUBLISHER")))
(unless (find-package "PATH_PUBLISHER::FLOATS")
  (make-package "PATH_PUBLISHER::FLOATS"))

(in-package "ROS")
;;//! \htmlinclude Floats.msg.html


(defclass path_publisher::Floats
  :super ros::object
  :slots (_index _length _data ))

(defmethod path_publisher::Floats
  (:init
   (&key
    ((:index __index) 0)
    ((:length __length) 0)
    ((:data __data) (make-array 0 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _index (round __index))
   (setq _length (round __length))
   (setq _data __data)
   self)
  (:index
   (&optional __index)
   (if __index (setq _index __index)) _index)
  (:length
   (&optional __length)
   (if __length (setq _length __length)) _length)
  (:data
   (&optional __data)
   (if __data (setq _data __data)) _data)
  (:serialization-length
   ()
   (+
    ;; int32 _index
    4
    ;; int32 _length
    4
    ;; float32[] _data
    (* 4    (length _data)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; int32 _index
       (write-long _index s)
     ;; int32 _length
       (write-long _length s)
     ;; float32[] _data
     (write-long (length _data) s)
     (dotimes (i (length _data))
       (sys::poke (elt _data i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; int32 _index
     (setq _index (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _length
     (setq _length (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; float32[] _data
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _data (instantiate float-vector n))
     (dotimes (i n)
     (setf (elt _data i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     ))
   ;;
   self)
  )

(setf (get path_publisher::Floats :md5sum-) "3399fec90a07c2467f8a8e04ebc2b5a5")
(setf (get path_publisher::Floats :datatype-) "path_publisher/Floats")
(setf (get path_publisher::Floats :definition-)
      "int32 index
int32 length
float32[] data
")



(provide :path_publisher/Floats "3399fec90a07c2467f8a8e04ebc2b5a5")


