package com.zhimian.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zhimian.entity.InterviewSession;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface InterviewSessionMapper extends BaseMapper<InterviewSession> {
    /** 同一会话的回答处理在数据库层串行化，跨应用实例同样生效。 */
    @Select("SELECT * FROM interview_session WHERE id = #{id} FOR UPDATE")
    InterviewSession selectByIdForUpdate(@Param("id") Long id);
}
