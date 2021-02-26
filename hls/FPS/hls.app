<project xmlns="com.autoesl.autopilot.project" name="FPS" top="farthest_point_sampling">
    <includePaths/>
    <libraryPaths/>
    <Simulation>
        <SimFlow name="csim" csimMode="2" lastCsimMode="0"/>
    </Simulation>
    <files xmlns="">
        <file name="../../fps_test.c" sc="0" tb="1" cflags=" -Wno-unknown-pragmas" csimflags=" -Wno-unknown-pragmas" blackbox="false"/>
        <file name="point_aux.h" sc="0" tb="false" cflags="" csimflags="" blackbox="false"/>
        <file name="point_aux.c" sc="0" tb="false" cflags="" csimflags="" blackbox="false"/>
        <file name="fps.h" sc="0" tb="false" cflags="" csimflags="" blackbox="false"/>
        <file name="fps.c" sc="0" tb="false" cflags="" csimflags="" blackbox="false"/>
    </files>
    <solutions xmlns="">
        <solution name="basic" status="inactive"/>
        <solution name="opt" status="active"/>
    </solutions>
</project>

